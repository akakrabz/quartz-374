---
title: "Worked problem — Designing a Turing machine"
description: "A one-tape Turing machine that decides {w#w : w ∈ {0,1}*}: the algorithm in English, a meaning for every state, the full transition table, traces on an accepted and a rejected input, why it halts on every input, and an exact step count showing Θ(n²) time."
tags: [problem, turing-machines]
---

*Problem · a Turing-machine design exercise (Chapter 6 material, on the final exam) · uses [[1-models-of-computation/06-turing-machines#62-formal-definitions|§6.2]], [[1-models-of-computation/06-turing-machines#63-a-first-example|§6.3]], [[1-models-of-computation/06-turing-machines#66-tracks-heads-and-tapes|§6.6]] · concepts: [[concepts/turing-machines]], [[concepts/acceptable-and-decidable]]*

> [!question] Problem
> Let $\textsf{Copy} = \{w\mathtt{\#}w \mid w\in\{\mathtt{0},\mathtt{1}\}^*\}$ over the input alphabet $\{\mathtt{0},\mathtt{1},\mathtt{\#}\}$. For example, `01#01` and `#` are in $\textsf{Copy}$; `01#10`, `0#0#` and $\varepsilon$ are not.
>
> (a) Describe a single-tape Turing machine that decides $\textsf{Copy}$: the algorithm in English, the states with their meanings, and the full transition table.
>
> (b) Trace your machine on `01#01`, and say where it rejects `01#00`.
>
> (c) Explain why it halts on every input, and show that its running time is $\Theta(n^2)$ for inputs of length $n$.

## (a) The machine

**Idea.** $\textsf{Copy}$ is not even context-free (a classic fact whose proof is beyond this course), so no grammar or stack can check it — but a [[concepts/turing-machines|Turing machine]] can, by comparing the two halves one symbol at a time and zigzagging across the `#`. It cannot remember $w$, but it can remember **one symbol** in its state and **mark** the symbols it has finished with.

> [!recipe] The algorithm in English
> Repeat rounds. In each round:
> 1. **Take** the leftmost unmarked symbol of the left half, overwrite it with `x`, and remember it in the state. If the `#` comes first instead, the left half is used up: go to step 5.
> 2. **Carry** it right, past the rest of the left half, to the `#`.
> 3. **Seek** past the marked symbols to the right of the `#` to the first unmarked one. It must be the remembered symbol: mark it with `x`. Anything else — the other symbol, a blank, a second `#` — means reject.
> 4. **Walk back** left, past the marked symbols and the `#`, then past the unmarked rest of the left half to the rightmost `x`; step right and start the next round.
> 5. **Check** that every symbol right of the `#` is marked: scan right over `x`s, accept at the first blank, reject at anything else.
>
> If the input has no `#`, step 2 runs into a blank: reject.

The tape alphabet is $\Gamma = \{\mathtt{0},\mathtt{1},\mathtt{\#},\mathtt{x},\square\}$. The states and what each one knows:

| state | meaning |
|---|---|
| $\textit{start}$ | the head is on the leftmost unmarked symbol of the left half, or on the `#` if there is none |
| $\mathit{carry0}$, $\mathit{carry1}$ | just marked a 0 (a 1) of the left half; moving right to the `#` |
| $\mathit{seek0}$, $\mathit{seek1}$ | right of the `#`, skipping marked symbols; the next unmarked symbol must be a 0 (a 1) |
| $\mathit{backR}$ | just marked the match; moving left through the right half to the `#` |
| $\mathit{backL}$ | moving left through the unmarked part of the left half to the rightmost `x` |
| $\mathit{check}$ | the left half is used up; every symbol right of the `#` must be marked |
| $\textit{accept}$, $\textit{reject}$ | halting states |

In the table, "—" means "write back the symbol that was read". **Missing transitions reject.**

| state | read | write | move | next state | comment |
|---|---|---|---|---|---|
| $\textit{start}$ | $\mathtt{0}$ | $\mathtt{x}$ | $+1$ | $\mathit{carry0}$ | take a 0 |
| | $\mathtt{1}$ | $\mathtt{x}$ | $+1$ | $\mathit{carry1}$ | take a 1 |
| | $\mathtt{\#}$ | — | $+1$ | $\mathit{check}$ | left half used up |
| $\mathit{carry0}$ | $\mathtt{0}$, $\mathtt{1}$ | — | $+1$ | $\mathit{carry0}$ | through the left half |
| | $\mathtt{\#}$ | — | $+1$ | $\mathit{seek0}$ | |
| $\mathit{carry1}$ | $\mathtt{0}$, $\mathtt{1}$ | — | $+1$ | $\mathit{carry1}$ | |
| | $\mathtt{\#}$ | — | $+1$ | $\mathit{seek1}$ | |
| $\mathit{seek0}$ | $\mathtt{x}$ | — | $+1$ | $\mathit{seek0}$ | skip matched symbols |
| | $\mathtt{0}$ | $\mathtt{x}$ | $-1$ | $\mathit{backR}$ | a match: mark it |
| $\mathit{seek1}$ | $\mathtt{x}$ | — | $+1$ | $\mathit{seek1}$ | |
| | $\mathtt{1}$ | $\mathtt{x}$ | $-1$ | $\mathit{backR}$ | |
| $\mathit{backR}$ | $\mathtt{x}$ | — | $-1$ | $\mathit{backR}$ | back to the `#` |
| | $\mathtt{\#}$ | — | $-1$ | $\mathit{backL}$ | |
| $\mathit{backL}$ | $\mathtt{0}$, $\mathtt{1}$ | — | $-1$ | $\mathit{backL}$ | back to the last `x` |
| | $\mathtt{x}$ | — | $+1$ | $\textit{start}$ | next round |
| $\mathit{check}$ | $\mathtt{x}$ | — | $+1$ | $\mathit{check}$ | |
| | $\square$ | — | $+1$ | $\textit{accept}$ | everything matched |

That is 20 transitions. The rejections are exactly the missing ones: $\textit{start}$ on $\square$ (the empty input has no `#`); $\mathit{carry0}$ or $\mathit{carry1}$ on $\square$ (no `#`); $\mathit{seek0}$ on `1` or $\mathit{seek1}$ on `0` (a mismatch); either $\mathit{seek}$ state on $\square$ (the right half is too short) or on `#` (a second `#`); $\mathit{check}$ on `0` or `1` (the right half is too long) or on `#` (a second `#`).

<!-- fig:prob2-copy-machine -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 690 396" width="690" height="396" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>state diagram with states start, carry0, carry1, seek0, seek1, backR, backL, check, accept</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="520" y="366" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">missing transitions go to reject</text><path d="M102.5,158 L201.4,93.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="147" y="115.8" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0/x,+1</text><path d="M101.5,190 L202.4,258.6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="146.8" y="234.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1/x,+1</text><path d="M79.2,190 L90.6,345.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="74" y="269.8" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">#;+1</text><path d="M220.5,61.9 C202.3,35.2 253.7,35.2 236.7,59.7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="228" y="26" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0,1;+1</text><path d="M235.5,290.1 C253.7,316.8 202.3,316.8 219.3,292.3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="228" y="326" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0,1;+1</text><path d="M259,76 L388.5,76" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="325" y="65" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">#;+1</text><path d="M259,276 L388.5,276" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="325" y="287" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">#;+1</text><path d="M410.5,61.9 C392.3,35.2 443.7,35.2 426.7,59.7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="418" y="26" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x;+1</text><path d="M425.5,290.1 C443.7,316.8 392.3,316.8 409.3,292.3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="418" y="326" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x;+1</text><path d="M445,91.4 L560.8,157.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="509.4" y="115.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0/x,−1</text><path d="M445,260 L560.9,191.3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="509.6" y="234.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1/x,−1</text><path d="M613.8,161.3 C640.1,142.5 640.1,205.5 616,187.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="651" y="174" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x;−1</text><path d="M563,174 L359.5,174" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="460" y="163" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">#;−1</text><path d="M322.5,159.9 C306.8,137.1 353.2,137.1 338.7,157.7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="330" y="126.9" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0,1;−1</text><path d="M303,174 L107.5,174" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="204" y="163" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x;+1</text><path d="M68.2,376.7 C45.8,393.1 45.8,334.9 66,350.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="33.9" y="364" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x;+1</text><path d="M119,364 L225.5,364" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="173.5" y="353" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">□;+1</text><line x1="25" y1="174" x2="48.5" y2="174" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><rect x="51" y="158" width="54" height="32" rx="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="78" y="175" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">start</text><rect x="197" y="60" width="62" height="32" rx="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="228" y="77" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">carry0</text><rect x="391" y="60" width="54" height="32" rx="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="418" y="77" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">seek0</text><rect x="197" y="260" width="62" height="32" rx="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="228" y="277" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">carry1</text><rect x="391" y="260" width="54" height="32" rx="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="418" y="277" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">seek1</text><rect x="303" y="158" width="54" height="32" rx="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="330" y="175" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">backL</text><rect x="563" y="158" width="54" height="32" rx="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="590" y="175" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">backR</text><rect x="65" y="348" width="54" height="32" rx="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="92" y="365" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">check</text><rect x="227" y="344" width="70" height="40" rx="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><rect x="231" y="348" width="62" height="32" rx="16" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="262" y="365" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">accept</text></svg><figcaption><strong>A Turing machine that decides {<i>w</i>#<i>w</i>}.</strong> Each round crosses off the next symbol of the left half (<i>start</i>), carries it across the # in the state (<i>carry0</i>/<i>carry1</i>), crosses off the matching symbol of the right half (<i>seek0</i>/<i>seek1</i>), and walks back (<i>backR</i>, then <i>backL</i>). A label <code>a/b,±1</code> means read <code>a</code>, write <code>b</code>, move; <code>0,1;−1</code> means read 0 or 1, leave it, move left.</figcaption></figure>

> [!trap] Design traps
> - **Falling off the left end.** $\mathit{backL}$ walks left until it sees an `x`, and that `x` always exists: cell 0 holds `x` from the machine's first move on (an input that starts with `#` never reaches $\mathit{backL}$). A machine that walks left "to the beginning of the tape" cannot see the beginning — it crashes there ([[1-models-of-computation/06-turing-machines#62-formal-definitions|§6.2]]).
> - **Junk inputs.** "Decides" means halting with the right answer on *every* input: $\varepsilon$, `0#`, `##`, `0#0#`, `01`, not just strings with mismatched halves. Here each of them ends in a missing transition; list the cases, as above, and test them.
> - **Silent missing transitions.** They reject only if you say so. Write "missing transitions go to reject" (the book's convention) — or give every transition.
> - **One mark for both halves.** Using the same `x` on both sides works because the `#` separates them and the marks of the left half form a prefix: the first `x` that $\mathit{backL}$ meets is the last symbol taken.

## (b) Traces

> [!example] Trace on `01#01`
> The underlined symbol is the one under the head. The machine accepts after 18 steps.
>
> | step | state | tape | step | state | tape |
> |---|---|---|---|---|---|
> | 0 | $\textit{start}$ | $\underline{\mathtt{0}}\mathtt{1\#01}$ | 10 | $\mathit{seek1}$ | $\mathtt{xx\#x}\underline{\mathtt{1}}$ |
> | 1 | $\mathit{carry0}$ | $\mathtt{x}\underline{\mathtt{1}}\mathtt{\#01}$ | 11 | $\mathit{backR}$ | $\mathtt{xx\#}\underline{\mathtt{x}}\mathtt{x}$ |
> | 2 | $\mathit{carry0}$ | $\mathtt{x1}\underline{\mathtt{\#}}\mathtt{01}$ | 12 | $\mathit{backR}$ | $\mathtt{xx}\underline{\mathtt{\#}}\mathtt{xx}$ |
> | 3 | $\mathit{seek0}$ | $\mathtt{x1\#}\underline{\mathtt{0}}\mathtt{1}$ | 13 | $\mathit{backL}$ | $\mathtt{x}\underline{\mathtt{x}}\mathtt{\#xx}$ |
> | 4 | $\mathit{backR}$ | $\mathtt{x1}\underline{\mathtt{\#}}\mathtt{x1}$ | 14 | $\textit{start}$ | $\mathtt{xx}\underline{\mathtt{\#}}\mathtt{xx}$ |
> | 5 | $\mathit{backL}$ | $\mathtt{x}\underline{\mathtt{1}}\mathtt{\#x1}$ | 15 | $\mathit{check}$ | $\mathtt{xx\#}\underline{\mathtt{x}}\mathtt{x}$ |
> | 6 | $\mathit{backL}$ | $\underline{\mathtt{x}}\mathtt{1\#x1}$ | 16 | $\mathit{check}$ | $\mathtt{xx\#x}\underline{\mathtt{x}}$ |
> | 7 | $\textit{start}$ | $\mathtt{x}\underline{\mathtt{1}}\mathtt{\#x1}$ | 17 | $\mathit{check}$ | $\mathtt{xx\#xx}\underline{\square}$ |
> | 8 | $\mathit{carry1}$ | $\mathtt{xx}\underline{\mathtt{\#}}\mathtt{x1}$ | 18 | $\textit{accept}$ | $\mathtt{xx\#xx}\square\underline{\square}$ |
> | 9 | $\mathit{seek1}$ | $\mathtt{xx\#}\underline{\mathtt{x}}\mathtt{1}$ | | | |

**Rejecting `01#00`.** The first round matches the two 0s exactly as above (steps 0–7, ending with $\textit{start}$ on cell 1 and tape $\mathtt{x1\#x0}$). In the second round $\mathit{carry1}$ crosses the `#`, $\mathit{seek1}$ skips the `x` in cell 3 and reads `0` in cell 4 at step 10, where it needs a 1. There is no transition for ($\mathit{seek1}$, `0`), so step 11 goes to $\textit{reject}$.

## (c) Halting and running time

**It halts on every input.** Each round marks one more symbol to the left of the first `#`, so there are at most $n$ rounds. Within a round, every phase moves in one direction and stops at a symbol that is guaranteed to be there, or rejects: $\mathit{carry}$ and $\mathit{seek}$ move right and reject on a blank, so they never pass cell $n$, the first blank; $\mathit{backR}$ stops at the `#` it crossed on the way right; $\mathit{backL}$ stops at an `x`. The final $\mathit{check}$ moves right and stops by cell $n$ as well.

**At most $O(n^2)$ steps.** A round sweeps right from its starting cell to at most cell $n$ and back, at most $2n+2$ steps; with at most $n$ rounds and a final scan of at most $n+2$ steps, the machine halts within $2n^2+3n+2$ steps on every input of length $n$.

**Exactly $2(k+1)^2$ steps on $w\mathtt{\#}w$.** Let $\lvert w\rvert = k$, so $n = 2k+1$. Round $i$ ($1\le i\le k$) starts on cell $i-1$:
- $\textit{start}$ marks $w_i$, and $\mathit{carry}$ crosses the other $k-i$ unmarked symbols of the left half and the `#`: $k-i+2$ steps;
- $\mathit{seek}$ crosses the $i-1$ marked symbols right of the `#` and marks the next one: $i$ steps;
- $\mathit{backR}$ crosses those $i-1$ marks and the `#`: $i$ steps;
- $\mathit{backL}$ crosses the $k-i$ unmarked symbols and reads the `x` on cell $i-1$: $k-i+1$ steps.

Every round therefore takes $2k+3$ steps, whatever $i$ is. The last phase — $\textit{start}$ reads the `#`, $\mathit{check}$ crosses $k$ marks and reads the blank — takes $k+2$. In all,
$$
k(2k+3) + k + 2 = 2k^2+4k+2 = 2(k+1)^2 = \frac{(n+1)^2}{2}\ \text{steps}.
$$
For `01#01` ($k = 2$) that is 18, as in the trace: rounds of 7 steps end at steps 7 and 14. Even lengths have no string $w\mathtt{\#}w$, but $w\mathtt{\#}w\mathtt{0}$ ($n = 2k+2$) runs the same $k$ rounds and is rejected when $\mathit{check}$ reads the final `0`: again $2(k+1)^2 = n^2/2$ steps.

> [!key] Answer (c)
> The machine halts on every input of length $n$ within $2n^2+3n+2$ steps, and on $w\mathtt{\#}w$ with $\lvert w\rvert = k$ it takes exactly $2(k+1)^2 = (n+1)^2/2$ steps (for even $n$, $w\mathtt{\#}w\mathtt{0}$ takes $n^2/2$). So its worst-case running time is $\Theta(n^2)$.

**Could a cleverer one-tape machine do better?** Not asymptotically. Every one-tape machine for $\textsf{Copy}$ needs $\Omega(n^2)$ steps in the worst case — the classic crossing-sequence argument, the same one behind the book's remark about marked palindromes in [[1-models-of-computation/06-turing-machines#66-tracks-heads-and-tapes|§6.6]] — while a machine with two tapes decides it in $O(n)$ time: copy $w$ to the second tape, then compare. The quadratic time is the price of a single head, not of a careless design.

> [!trap] Time-analysis traps
> - **Counting rounds only.** There are about $n/2$ rounds, and each one walks across the `#` and back, about $n$ steps: $\Theta(n)$ rounds of $\Theta(n)$ steps.
> - **$\Theta$ needs both bounds.** The $O(n^2)$ upper bound alone is not $\Theta(n^2)$; the exact count on $w\mathtt{\#}w$ supplies the matching lower bound.
> - **$n$ is the whole input length,** `#` included: $n = 2k+1$ for $w\mathtt{\#}w$.

> [!exam] On the exams
> Turing machines (Chapter 6) are tested on the final exam only. The course's standard rubrics have no separate entry for Turing-machine design, so take the DFA rubric's demands as the guide: a complete, unambiguous description — every state with its meaning, every transition or an explicit "missing transitions reject" — plus a check of the edge cases ($\varepsilon$, no `#`, two `#`s, halves of different lengths). Describe the algorithm in English first; the table is then routine.

### Sources for this page
$\{w\mathtt{\#}w\}$ is a classic example language for Turing machines (and a standard example of a decidable language that is not context-free); the machine, its table, the traces and the exact step count are ours, in the conventions of Erickson, *Models of Computation*, §§6.2–6.3. The $\Omega(n^2)$ lower bound for one-tape machines is a classic crossing-sequence result, cited here and not proved; the book states the analogous fact for marked palindromes in §6.6. Checked by `tools/checks/problems_2.py`: the machine accepts exactly $\textsf{Copy}$ and halts on all 88,573 inputs over $\{\mathtt{0},\mathtt{1},\mathtt{\#}\}$ of length at most 10, within the stated bound; it takes $2(k+1)^2$ steps on every $w\mathtt{\#}w$ with $k\le7$, in rounds of $2k+3$ steps, and as many on every $w\mathtt{\#}w\mathtt{0}$; and both traces are as shown.
