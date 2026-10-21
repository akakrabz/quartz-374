---
title: "Chapter 1 exercises — Recursion"
description: "Solutions to selected exercises from Chapter 1 of Erickson's Algorithms: non-recursive Tower of Hanoi algorithms, the Baguenaudier, the Towers of Pisa, restricted Hanoi puzzles, recursion-tree recurrences, pancake sorting, median-of-three quicksort, StoogeSort, Cruel and Unusual, and counting inversions."
tags: [exercises, algorithms, recursion, midterm-2]
---

*Solved exercises for [[2-algorithms/01-recursion|Chapter 1]] · book pp. 44–70 · statements paraphrased; see the book for the originals*

These are Exercises 1–13 of the chapter, minus the hard parts: 1.1 (all four parts), 1.2(b–c), 1.3, 1.4(a), 1.5(a–b), 1.6, 1.7, 1.8, 1.9, 1.10(a), 1.11, 1.12(b–e) and 1.13. Skipped: 1.2(a) (◆, needs graphs), 1.4(b–c) (♣♥), 1.5(c–e) and 1.10(b) (♥), 1.12(a) (a long argument via the 0–1 principle for oblivious sorting), and Exercises 14 onward. Exercise 1.8 carries a ♥ in the book but is a recursion-tree drill worth knowing, so it is here. Three statements needed repair — 1.1(b), 1.1(d) and a remark in 1.5(a) — and each solution says how. Algorithms are written to the [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|recursive-algorithm rubric]]: what the recursive procedure solves (including any generalization), base cases, recursive calls, how their results combine, and the recurrence with its solution ([[concepts/recursion]], [[concepts/recursion-trees]]).

## Exercise 1.1 — Tower of Hanoi without recursion

> [!question] Exercise 1.1 (book pp. 44–45)
> Prove that the recursive Tower of Hanoi algorithm of [[2-algorithms/01-recursion#13-tower-of-hanoi|§1.3]] makes exactly the same moves — same disks, same pegs, same order — as each of the following non-recursive algorithms. The pegs are 0, 1, 2, and $n$ disks move from peg 0 to peg 2.
>
> **(a)** If $n$ is even, swap the names of pegs 1 and 2. At the $i$th step, make the only legal move that avoids peg $i \bmod 3$. If there is no legal move, all disks are on peg $i \bmod 3$ and the puzzle is solved.
>
> **(b)** For the first move, move disk 1 to peg 1 if $n$ is even and to peg 2 if $n$ is odd. Then repeatedly make the only legal move that involves a different disk from the previous move. If no such move exists, the puzzle is solved.
>
> **(c)** Pretend that disks $n+1$, $n+2$, $n+3$ sit at the bottom of pegs 0, 1, 2. Repeatedly make the only legal move that never places an odd disk directly on an odd disk, never places an even disk directly on an even disk, and does not undo the previous move, until no such move exists.
>
> **(d)** Let the *ruler function* $\rho(n)$ be the smallest $k$ such that $n/2^k$ is not an integer (so $\rho(42)=2$; equivalently, one more than the position of the lowest 1 bit of $n$). The algorithm:
> ```text
> RulerHanoi(n):
>   i ← 1
>   while ρ(i) ≤ n
>     if n − i is even
>       move disk ρ(i) forward       ⟨⟨0 → 1 → 2 → 0⟩⟩
>     else
>       move disk ρ(i) backward      ⟨⟨0 → 2 → 1 → 0⟩⟩
>     i ← i + 1
> ```

### Two facts about the recursive algorithm

The book's algorithm is $\textsf{Hanoi}(n, \textit{src}, \textit{dst}, \textit{tmp})$: move $n-1$ disks src → tmp recursively, move disk $n$ src → dst, move $n-1$ disks tmp → dst recursively. Call a move **forward** if it goes from peg $p$ to peg $p+1 \bmod 3$ and **backward** if it goes to $p-1 \bmod 3$. All four parts rest on two facts about $\textsf{Hanoi}(n, 0, 2, 1)$.

> [!key] Facts H1 and H2
> - **H1.** Move number $i$ moves disk $\rho(i)$. So disk 1 makes exactly the odd-numbered moves, and the moves alternate between disk 1 and some other disk.
> - **H2.** Disk $k$ always moves in the same direction: **backward if $n-k$ is even, forward if $n-k$ is odd.**

> [!proof]- Proof of H1 and H2
> **H1**, by induction on $n$. The moves are a call on $n-1$ disks ($2^{n-1}-1$ moves), then disk $n$ (move number $2^{n-1}$, and $\rho(2^{n-1}) = n$), then a second call on $n-1$ disks. Which disk a move moves does not depend on the peg names, so by the induction hypothesis move $i < 2^{n-1}$ moves disk $\rho(i)$, and move $2^{n-1}+j$ with $1 \le j < 2^{n-1}$ moves disk $\rho(j) = \rho(2^{n-1}+j)$: adding $2^{n-1}$ to a number below $2^{n-1}$ does not change its lowest 1 bit.
>
> **H2.** Give each call $\textsf{Hanoi}(m, s, d, t)$ the direction of $s \to d$. Because $\{s, d, t\} = \{0, 1, 2\}$, if $d = s+1$ then $t = s-1$, so the subcalls $s \to t$ and $t \to d$ are both backward; symmetrically, if $s \to d$ is backward both subcalls are forward. So each level of recursion flips the direction. Disk $k$ is moved only by calls on $k$ disks, which are $n-k$ levels below the top call $0 \to 2$, a backward move. $\blacksquare$

### (a) Avoid peg i mod 3

> [!hint]- Hint
> Disk 1 makes the odd moves and goes around the pegs in one direction, which tells you the peg it avoids. On an even step, the move cannot touch the peg holding disk 1.

> [!solution]- Solution
> Use the peg names the algorithm uses. For odd $n$, disk 1 moves backward (H2: $n-1$ is even). For even $n$ it moves forward, $0 \to 1 \to 2 \to 0$, which after swapping the names 1 and 2 reads $0 \to 2 \to 1 \to 0$: backward again. So in the algorithm's names disk 1 always moves backward, and after $j$ moves it sits on peg $-j \bmod 3$. We show by induction on $i$ that step $i$ of the algorithm is Hanoi's move $i$.
> - **Odd step $i = 2j-1$.** Hanoi moves disk 1 (H1), from peg $-(j-1)$ to peg $-j$. The three pegs sum to $0 \pmod 3$, so the third peg is $(j-1) + j = i \pmod 3$: Hanoi's move avoids peg $i \bmod 3$. Between the other two pegs the only legal move is disk 1's, because disk 1 is on top of one of them and is the smallest disk.
> - **Even step $i = 2j$.** Disk 1 has moved $j$ times and sits on peg $-j \equiv 2j = i \pmod 3$. Hanoi moves another disk (H1), and that move cannot involve disk 1's peg: nothing can be taken from under disk 1 or put on it. Between two given pegs at most one move is legal, so the algorithm again makes Hanoi's move.
> - **Stopping.** Until Hanoi is done, its next move is available, so the algorithm does not stop early. After $2^n - 1$ steps all disks are on the target, and step $2^n$ avoids peg $2^n \equiv (-1)^n \pmod 3$ — that is 2 for odd $n$, and 1, the new name of peg 2, for even $n$. The other two pegs are empty, so there is no legal move and the algorithm stops.
>
> **Answer.** Disk 1 makes every odd move, always backward in the algorithm's names, so the odd steps avoid exactly the right peg; every even move avoids disk 1's peg, which is peg $i \bmod 3$. Both force Hanoi's move, and the algorithm stops right after move $2^n-1$.

### (b) Never the same disk twice in a row

> [!hint]- Hint
> The moves alternate between disk 1 and another disk. After a move of disk 2, count the legal moves that do not move disk 2.

> [!solution]- Solution
> **As printed, the rule is ambiguous.** For $n = 2$: disk 1 goes to peg 1, then the only other legal move takes disk 2 from peg 0 to peg 2 — and now disk 1 may legally go to peg 0 *or* to peg 2, both "a different disk from the previous move". In general, after a move of disk $k \ge 2$ from peg $a$ to peg $b$, disk 1 sits on the third peg and can go to either $a$ or $b$. The rule needs one more clause: **disk 1 never returns to the peg it just left** (equivalently, it keeps going around in the direction of its first move). With it, we show by induction that the algorithm makes Hanoi's moves.
> - **First move.** Disk 1 goes $0 \to 1$ (forward) for even $n$ and $0 \to 2$ (backward) for odd $n$ — Hanoi's first move, by H1 and H2.
> - **After a move of disk 1**, the rule moves another disk. That move cannot touch disk 1's peg, and between the other two pegs at most one move is legal. Hanoi's next move is of this kind (H1), so the rule makes it.
> - **After a move of disk $k \ge 2$** from $a$ to $b$, the only legal moves of a disk other than $k$ are disk 1's two moves: the top of $a$ is larger than $k$ and larger than disk 1. The extra clause removes one; the other continues disk 1's cycle, which is Hanoi's next move by H1 and H2.
> - **Stopping.** Hanoi's last move, number $2^n - 1$, moves disk 1 onto the full stack on peg 2. The rule now needs a move of another disk, and pegs 0 and 1 are empty, so it stops. Before that, Hanoi's next move is always available.
>
> **Answer.** With "disk 1 never moves back to the peg it just left" added, the moves alternate between disk 1, cycling in a fixed direction, and the unique legal move not involving disk 1 — exactly Hanoi's sequence.

### (c) The odd–even rule

> [!hint]- Hint
> First show that Hanoi never puts a disk directly on a disk of the same parity. Then count the parities of the three top disks: exactly two of them are odd, so only two moves obey the parity rules.

> [!solution]- Solution
> The pretend disks never move.
>
> **Claim 1: Hanoi obeys the parity rules.** Whenever $\textsf{Hanoi}(m,s,d,t)$ is called, the disk directly under the moving stack on $s$ and the top disk of $d$ have parity opposite to $m$, and the top disk of $t$ has the parity of $m$. This holds for the first call (disks $n+1$, $n+3$, $n+2$), and it passes to the subcalls. In $\textsf{Hanoi}(m-1, s, t, d)$ the disk under the stack is disk $m$, the target's top is $t$'s top (parity of $m$), the spare's top is $d$'s top (parity opposite to $m$). In $\textsf{Hanoi}(m-1, t, d, s)$ the disk under the stack is $t$'s old top (parity of $m$), the target's top is disk $m$, the spare's top is the disk that was under disk $m$ (parity opposite to $m$). Measured against $m-1$, each has the required parity. So disk $m$ always lands on a disk of opposite parity, and every peg alternates in parity from bottom to top.
>
> **Claim 2: exactly two tops are odd.** On an alternating peg with bottom disk $b$ and $h$ real disks, the top has the parity of $b + h$. Summed over the three pegs, $(n+1) + (n+2) + (n+3) + n$ is even, so an even number of tops are odd. Disk 1 is a top and is odd, so one other top is odd and one is even. The moves allowed by the parity rules are therefore exactly:
> - $(\alpha)$ disk 1 onto the even top;
> - $(\beta)$ the one size-legal move between the two pegs not holding disk 1 (their tops have opposite parities), if either of them holds a real disk.
>
> **Induction: step $i$ is Hanoi's move $i$.** The position is Hanoi's, so both claims apply.
> - At the start, pegs 1 and 2 hold only pretend disks, so only $(\alpha)$ exists: disk 1 goes onto the even one of $n+2$, $n+3$ — peg 1 for even $n$, peg 2 for odd $n$, as in Hanoi.
> - If the previous move took disk 1 off peg $P$, disk 1 had been sitting on an even disk, which is now $P$'s top: $(\alpha)$ would undo the previous move. Only $(\beta)$ is left. By H1 Hanoi's next move is not a move of disk 1, and $(\beta)$ is the only such legal move.
> - If the previous move was $(\beta)$, taking disk $k$ from $P$ to $R$, then the size-legal move between $P$ and $R$ is now $k$ back to $P$: $(\beta)$ would undo it. Only $(\alpha)$ is left. Hanoi's next move moves disk 1 (H1) and obeys the parity rules (Claim 1), so it is $(\alpha)$.
> - When Hanoi is done, its last move was disk 1's, so $(\alpha)$ is an undo, and pegs 0 and 1 hold only pretend disks, so $(\beta)$ does not exist. The algorithm stops exactly then.
>
> **Answer.** Hanoi keeps every peg alternating in parity, so at each moment exactly two moves obey the parity rules, and "do not undo" always removes the one Hanoi does not make.

### (d) RulerHanoi

> [!hint]- Hint
> H1 says which disk moves at step $i$ and H2 says in which direction. Compare with the printed test, starting with $n = 1$.

> [!solution]- Solution
> **The printed test is wrong.** For $n = 1$ it moves disk 1 forward, from peg 0 to peg 1, but the puzzle needs $0 \to 2$. By H2 the direction of disk $\rho(i)$ depends on $n - \rho(i)$, not on $n - i$, and it is backward when that number is even. Corrected loop body:
> ```text
>     if n − ρ(i) is odd
>       move disk ρ(i) forward       ⟨⟨0 → 1 → 2 → 0⟩⟩
>     else
>       move disk ρ(i) backward      ⟨⟨0 → 2 → 1 → 0⟩⟩
> ```
> **Proof for the corrected version.** By H1, Hanoi's move $i$ moves disk $\rho(i)$; by H2 that disk moves forward exactly when $n - \rho(i)$ is odd. A disk and a direction determine the move, so step $i$ of RulerHanoi is Hanoi's move $i$. The loop runs while $\rho(i) \le n$, that is, while $2^n$ does not divide $i$: exactly for $i = 1, \dots, 2^n - 1$, the length of Hanoi's sequence.
>
> **Answer.** With "forward if $n - \rho(i)$ is odd, backward if it is even", RulerHanoi makes Hanoi's moves; the printed test "$n - i$ even means forward" already fails for $n = 1$.

## Exercise 1.2 — The Baguenaudier

> [!question] Exercise 1.2 (book pp. 45–46)
> Model the Chinese rings puzzle as a string of $n$ bits, indexed $1, \dots, n$ from the right. Two moves are legal: flip bit 1 (always), and, if the string ends with exactly $z$ zeros, flip bit $z+2$. The goal is to turn $\mathtt{1}^n$ into $\mathtt{0}^n$; for $n = 5$ the 21 flips $1,3,1,2,1,5,1,2,1,3,1,2,1,4,1,2,1,3,1,2,1$ do it. A sequence of moves is **reduced** if no move is the inverse of the previous one — here, no bit is flipped twice in a row.
>
> (a) *Skipped (◆).* Prove that exactly one reduced sequence solves the $n$-ring puzzle.
>
> **(b)** Describe an algorithm that, given $n$, prints a reduced sequence of moves solving the puzzle; for $n = 5$ it should print the sequence above.
>
> **(c)** Exactly how many moves does your algorithm print, as a function of $n$? Prove it.

### (b) Printing a solution

> [!hint]- Hint
> To flip bit $n$ you need bit $n-1$ set and every bit below it clear. Clear the low $n-2$ bits, flip bit $n$, set the low $n-2$ bits again, and clear the low $n-1$ bits.

> [!solution]- Solution
> Flipping bit $j \ge 2$ is legal exactly when bit $j-1$ is 1 and bits $1, \dots, j-2$ are 0. Legality depends only on the bits *below* the flipped one, so a sequence that touches only bits $1..k$ works whatever the higher bits are.
>
> **What the recursion solves.** $\textsf{Off}(k)$ prints a reduced sequence turning bits $1..k$ from all 1s into all 0s; $\textsf{On}(k)$ prints a reduced sequence turning them from all 0s into all 1s, namely the output of $\textsf{Off}(k)$ in reverse order (each move is its own inverse, so a legal sequence read backwards is legal and goes the other way). Higher bits are never touched. The answer is $\textsf{Off}(n)$.
> ```text
> Off(k):
>   if k = 1
>     print 1
>   else if k ≥ 2
>     Off(k − 2)
>     print k
>     On(k − 2)
>     Off(k − 1)
> ```
> **Base cases.** $k = 0$: nothing to print. $k = 1$: flipping bit 1 is always legal.
>
> **Recursive calls.** After $\textsf{Off}(k-2)$, bits $k..1$ read $\mathtt{11}\,\mathtt{0}^{k-2}$: the string ends with exactly $k-2$ zeros, so flipping bit $k$ is legal. Then $\textsf{On}(k-2)$ leaves $\mathtt{0}\,\mathtt{1}^{k-1}$, and $\textsf{Off}(k-1)$ clears bits $1..k-1$.
>
> **Reduced.** By induction, the first move of $\textsf{Off}(k)$ is 1 for odd $k$ and 2 for even $k$ ($\textsf{Off}(k)$ starts with $\textsf{Off}(k-2)$ when $k \ge 3$). Each piece is reduced by induction (reversal keeps a sequence reduced). At the joints: the moves next to "print $k$" flip bits at most $k-2$; and the last move of $\textsf{On}(k-2)$ is the first move of $\textsf{Off}(k-2)$, whose parity is that of $k$, while $\textsf{Off}(k-1)$ starts with a move of the other parity. (For $k = 2$ the output is just $2, 1$.)
>
> For $n = 5$ the output is $\textsf{Off}(3) = 1,3,1,2,1$, then $5$, then $\textsf{On}(3) = 1,2,1,3,1$, then $\textsf{Off}(4) = 2,1,4,1,2,1,3,1,2,1$ — the book's sequence.
>
> **Answer.** $\textsf{Off}(n)$: clear the low $n-2$ rings, flip ring $n$, put the low $n-2$ rings back (the same moves in reverse), then clear the low $n-1$ rings.

### (c) Exactly how many moves

> [!hint]- Hint
> Write the recurrence from the four lines of $\textsf{Off}$, compute a few values, and compare them with powers of 2.

> [!solution]- Solution
> Let $M(k)$ be the number of moves printed by $\textsf{Off}(k)$, which is also the number printed by $\textsf{On}(k)$. From the algorithm,
> $$
> M(0) = 0, \qquad M(1) = 1, \qquad M(k) = M(k-1) + 2M(k-2) + 1 \quad (k \ge 2),
> $$
> giving $0, 1, 2, 5, 10, 21, 42, 85, \dots$
>
> **Claim.** $M(n) = \lfloor 2^{n+1}/3 \rfloor$: that is, $(2^{n+1}-2)/3$ for even $n$ and $(2^{n+1}-1)/3$ for odd $n$.
>
> *Proof by induction.* True for $n = 0, 1$. For $n \ge 2$, plug the claim for $n-1$ and $n-2$ (which have opposite parities) into the recurrence:
> $$
> \begin{aligned}
> n \text{ even:}\quad M(n) &= \frac{2^n - 1}{3} + 2 \cdot \frac{2^{n-1} - 2}{3} + 1 = \frac{2^{n+1} - 2}{3}, \\[6pt]
> n \text{ odd:}\quad M(n) &= \frac{2^n - 2}{3} + 2 \cdot \frac{2^{n-1} - 1}{3} + 1 = \frac{2^{n+1} - 1}{3}. \qquad \blacksquare
> \end{aligned}
> $$
>
> **Answer.** $\lfloor 2^{n+1}/3 \rfloor$ moves — 21 for $n = 5$.

## Exercise 1.3 — The Towers of Pisa

> [!question] Exercise 1.3 (book pp. 46–47)
> Tower of Hanoi with two vertical needles and one leaning needle. A larger disk may never sit on a smaller one, and disks are moved *onto* the leaning needle, or between the two vertical needles, one at a time — but **any number of disks from the top of the leaning needle may be moved together, in a single move, to another needle**. Describe an algorithm that moves a stack of $n$ disks from one vertical needle to the other using the smallest possible number of moves. Exactly how many moves does it make?

> [!hint]- Hint
> To move the largest disk, park the other $n-1$ disks on the leaning needle; afterwards one move brings them all onto it. Parking a stack on the leaning needle is a second problem, solved by the same idea.

> [!solution]- Solution
> Call the vertical needles $A$, $B$ and the leaning needle $L$. In both procedures every disk below the moving stack is larger than all the moving disks, so it can be ignored.
>
> **What the recursion solves.** $\textsf{Transfer}(m, A, B)$ moves the top $m$ disks from vertical needle $A$ to vertical needle $B$. $\textsf{Park}(m, A, B)$ moves the top $m$ disks from vertical needle $A$ onto $L$, using $B$ as the spare. The answer is $\textsf{Transfer}(n, A, B)$.
> ```text
> Transfer(m, A, B):
>   if m = 1
>     move disk 1 from A to B
>   else if m ≥ 2
>     Park(m − 1, A, B)
>     move disk m from A to B
>     move disks 1 .. m−1 together from L to B
>
> Park(m, A, B):
>   if m ≥ 1
>     Transfer(m − 1, A, B)
>     move disk m from A to L
>     Park(m − 1, B, A)
> ```
> **Base cases.** $\textsf{Transfer}(1)$ is one move; $\textsf{Transfer}(0)$ and $\textsf{Park}(0)$ do nothing.
>
> **Recursive calls and combination.** When disk $m$ moves, the $m-1$ smaller disks are all on the third needle, so the move is legal. After $\textsf{Park}(m-1, A, B)$, disks $1..m-1$ are the top of $L$ in order, so they leave together in one move. In $\textsf{Park}$, the second call stacks disks $1..m-1$ onto disk $m$ on $L$.
>
> **Count.** With $T(m)$ and $S(m)$ the moves of $\textsf{Transfer}$ and $\textsf{Park}$:
> $$
> \begin{aligned}
> T(1) &= 1, & T(m) &= S(m-1) + 2 && (m \ge 2), \\
> S(0) &= 0, & S(m) &= T(m-1) + 1 + S(m-1) && (m \ge 1).
> \end{aligned}
> $$
> Substituting the first into the second, $S(m) = S(m-1) + S(m-2) + 3$ for $m \ge 3$, with $S(1) = 1$ and $S(2) = 3$. So $S(m) + 3$ follows the Fibonacci recurrence, starting at $4 = 2F_3$ and $6 = 2F_4$ (with $F_1 = F_2 = 1$): $S(m) = 2F_{m+2} - 3$. Then
> $$
> T(n) = 2F_{n+1} - 1 \qquad (n \ge 1),
> $$
> which is $1, 3, 5, 9, 15, 25, 41$ for $n = 1, \dots, 7$ — $\Theta(\phi^n)$ with $\phi = (1+\sqrt5)/2$, against $2^n - 1$ in Benares. For $n = 7$ the first seven moves are exactly those drawn in the book's Figure 1.17; the fifth carries disks 1 and 2 off the leaning needle.
>
> **Optimality.** An exhaustive search over all positions shows that no shorter solution exists for $n \le 9$. A general proof needs a case analysis of how the largest disk can reach its target and is not given here.
>
> **Answer.** Park $n-1$ disks on the leaning needle, move disk $n$, and bring the $n-1$ disks back in one move: $2F_{n+1} - 1$ moves.

## Exercise 1.4 — Hanoi through peg 0

> [!question] Exercise 1.4 (book pp. 47–48)
> Restricted Tower of Hanoi puzzles; as in Exercise 1.1, $n$ disks move from peg 0 to peg 2.
>
> **(a)** No disk may move directly between pegs 1 and 2: every move involves peg 0. Describe an algorithm that solves the puzzle in as few moves as possible. Exactly how many moves does it make?
>
> (b) *Skipped (♣♥).* Only the moves $0 \to 2$, $2 \to 1$ and $1 \to 0$ are allowed.
>
> (c) *Skipped (♣♥).* Only the move $0 \to 2$ is forbidden.

### (a) Every move involves peg 0

> [!hint]- Hint
> Line the pegs up in the order 1, 0, 2: peg 0 is in the middle, and the stack starts on it. You also need a procedure that carries a stack from one end of the row to the other.

> [!solution]- Solution
> Line the pegs up in the order 1, 0, 2; then disks move only between neighbors, and peg 0 is in the middle. Disks below the moving stack are larger and can be ignored.
>
> **What the recursion solves.** $\textsf{Across}(m, x, y)$ moves the top $m$ disks from end peg $x$ to the other end peg $y$, through peg 0. $\textsf{Out}(m, y)$ moves the top $m$ disks from peg 0 to end peg $y$ ($x$ denotes the other end peg). The answer is $\textsf{Out}(n, 2)$.
> ```text
> Across(m, x, y):
>   if m > 0
>     Across(m − 1, x, y)
>     move disk m from x to 0
>     Across(m − 1, y, x)
>     move disk m from 0 to y
>     Across(m − 1, x, y)
>
> Out(m, y):
>   if m > 0
>     Out(m − 1, x)
>     move disk m from 0 to y
>     Across(m − 1, x, y)
> ```
> **Base case** $m = 0$: nothing. **Recursive calls.** Every move of disk $m$ happens while all smaller disks sit on the third peg, so it is legal, and every move involves peg 0.
>
> **Count.** $A(0) = 0$ and $A(m) = 3A(m-1) + 2$, so $A(m) = 3^m - 1$. $O(0) = 0$ and $O(m) = O(m-1) + 1 + A(m-1) = O(m-1) + 3^{m-1}$, so
> $$
> O(n) = 1 + 3 + \dots + 3^{n-1} = \frac{3^n - 1}{2}.
> $$
> **No algorithm does better.** The moves of the smaller disks, taken alone, solve a smaller puzzle (larger disks never block smaller ones), so lower bounds add up. *Across:* disk $m$ must go $x \to 0$ and later $0 \to y$. At its first move all smaller disks are on $y$; at its last move they are all on $x$; at the end they are on $y$. So they travel $x \to y$, $y \to x$, $x \to y$: at least $3A(m-1) + 2$ moves in total. *Out:* the last move of disk $m$ is $0 \to y$, and then all smaller disks are on $x$. They got there from peg 0 (at least $O(m-1)$ moves) and must still go from $x$ to $y$ (at least $A(m-1)$): at least $O(m-1) + 1 + A(m-1)$.
>
> **Answer.** Move $n-1$ disks to peg 1, disk $n$ to peg 2, then the $n-1$ disks from peg 1 to peg 2 through peg 0: $(3^n - 1)/2$ moves, which is optimal.

## Exercise 1.5 — Hanoi on a row of pegs

> [!question] Exercise 1.5 (book p. 48)
> A row of $k$ pegs is numbered $1, \dots, k$. In one move you take the top disk of some peg $i$ and put it on peg $i-1$ or $i+1$, never on a smaller disk. The task is to move a stack of $n$ disks from peg 1 to peg $k$.
>
> **(a)** Describe a recursive algorithm for $k = 3$. Exactly how many moves does it make? (The book adds: "This is exactly the same as problem 4(a).")
>
> **(b)** Describe a recursive algorithm for $k = n+1$ that makes at most $O(n^3)$ moves. [Hint: use part (a).]
>
> (c)–(e) *Skipped (♥).* $O(n^2)$ moves for $k = n+1$; polynomially many for $k = \sqrt n$; general $n$ and $k$.

### (a) Three pegs in a row

> [!hint]- Hint
> The largest disk must stop on the middle peg on its way. Where are all the other disks at that moment?

> [!solution]- Solution
> This is $\textsf{Across}(n, 1, 3)$ from Exercise 1.4(a), with the middle peg 2 in the role of peg 0: move $n-1$ disks $1 \to 3$, disk $n$ $1 \to 2$, $n-1$ disks $3 \to 1$, disk $n$ $2 \to 3$, $n-1$ disks $1 \to 3$. Base case $n = 0$: nothing. The recurrence $A(n) = 3A(n-1) + 2$, $A(0) = 0$, gives
> $$
> A(n) = 3^n - 1,
> $$
> and the lower-bound argument of 1.4(a) shows that no algorithm does better.
>
> **Not quite the same as 4(a).** In 4(a) the stack starts on the *middle* peg (peg 0 is the middle of the row 1, 0, 2), so that puzzle takes only $(3^n-1)/2$ moves. Part (a) here, end to end, is the subroutine $\textsf{Across}$ of 4(a). For $n = 1$: one move there, two here.
>
> **Answer.** $3^n - 1$ moves.

### (b) n + 1 pegs in cubic time

> [!hint]- Hint
> A small disk can hop over a large one by stepping onto it and off again. Spread the small disks out to the right, let the largest disk walk to the last peg while each small disk hops over it back to peg 1, then recurse on the $n-1$ disks now stacked on peg 1.

> [!solution]- Solution
> A peg holding only disks larger than $m$ behaves like an empty peg for disks $1..m$. That suggests the generalization:
>
> **What the recursion solves.** For $d \ge m$, $\textsf{Shift}(m, a, d)$ moves disks $1..m$, stacked on peg $a$, to peg $a + d$, provided pegs $a+1, \dots, a+d$ hold no disk smaller than $m+1$. The answer is $\textsf{Shift}(n, 1, n)$ on pegs $1..n+1$. ("Walk" a disk = move it one peg at a time.)
> ```text
> Shift(m, a, d):
>   if m ≥ 1
>     for i ← 1 to m − 1                          ⟨⟨spread out⟩⟩
>       walk disk i from peg a to peg a + d + 1 − i
>     for p ← a to a + d − 1                      ⟨⟨disk m walks right⟩⟩
>       if peg p + 1 holds a disk i < m
>         walk disk i from peg p + 1 to peg a     ⟨⟨hop over disk m⟩⟩
>       move disk m from peg p to peg p + 1
>     Shift(m − 1, a, d)
> ```
> **Base case** $m = 0$: nothing to move.
>
> **Spread.** Disk $i$ walks over pegs holding no small disk (disks $1..i-1$ are already further right) and stops on peg $a+d+1-i$. Disk $m-1$ stops on peg $a+d-m+2 \ge a+2$, so peg $a+1$ stays free.
>
> **Walk.** When disk $m$ stands on peg $p$ and the next peg holds disk $i$ (the largest small disk still to its right), disk $i$ steps onto disk $m$ — legal, since $i < m$ — and walks on, over empty pegs, to peg $a$, where only larger small disks are waiting. Then disk $m$ steps right. In the end disk $m$ is on peg $a+d$ and disks $m-1, \dots, 1$ are stacked in order on peg $a$.
>
> **Recursive call.** $\textsf{Shift}(m-1, a, d)$ moves that stack to peg $a+d$, onto disk $m$, which acts as an empty peg for it.
>
> **Count.** The spread and the hops each cost $\sum_{i=1}^{m-1} (d+1-i)$ moves, and disk $m$ makes $d$:
> $$
> M(m) = M(m-1) + d + (m-1)(2d + 2 - m), \qquad M(0) = 0.
> $$
> With $d = n$ each round costs $O(n^2)$ and there are $n$ rounds, so $M(n) = O(n^3)$; exactly,
> $$
> M(n) = \frac{2n^3 + 3n^2 - 2n}{3},
> $$
> which is $1, 8, 25, 56$ for $n = 1, 2, 3, 4$ (for $n = 2$ this is part (a)'s $3^2 - 1$). This solution does not need part (a).
>
> **Answer.** Spread the $n-1$ small disks out, walk disk $n$ to peg $n+1$ while the small disks hop back over it to peg 1, and recurse: $(2n^3 + 3n^2 - 2n)/3 = O(n^3)$ moves.

## Exercise 1.6 — Nine recurrences

> [!question] Exercise 1.6 (book p. 49)
> Use recursion trees ([[2-algorithms/01-recursion#17-recursion-trees|§1.7]]) to solve each of the following recurrences.
> $$
> \begin{array}{lll}
> A(n) = 2A(n/4) + \sqrt n & B(n) = 2B(n/4) + n & C(n) = 2C(n/4) + n^2 \\
> D(n) = 3D(n/3) + \sqrt n & E(n) = 3E(n/3) + n & F(n) = 3F(n/3) + n^2 \\
> G(n) = 4G(n/2) + \sqrt n & H(n) = 4H(n/2) + n & I(n) = 4I(n/2) + n^2
> \end{array}
> $$

> [!hint]- Hint
> For $T(n) = a\,T(n/b) + n^c$ the level sums form a geometric series with ratio $a/b^c$. Compare the ratio with 1.

> [!solution]- Solution
> In the tree for $T(n) = a\,T(n/b) + n^c$, level $i$ has $a^i$ nodes of size $n/b^i$, so it sums to $a^i (n/b^i)^c = n^c (a/b^c)^i$; there are $\log_b n$ levels above the $a^{\log_b n} = n^{\log_b a}$ leaves. Ratio below 1: the root dominates, $\Theta(n^c)$. Ratio 1: all $\Theta(\log n)$ levels are equal, $\Theta(n^c \log n)$. Ratio above 1: the leaves dominate, $\Theta(n^{\log_b a})$.
>
> | | ratio $a/b^c$ | level sums | dominated by | solution |
> |---|---|---|---|---|
> | $A$ | $2/\sqrt4 = 1$ | all $\sqrt n$ | all $\log_4 n$ levels | $\Theta(\sqrt n \log n)$ |
> | $B$ | $2/4 = 1/2$ | decreasing | root | $\Theta(n)$ |
> | $C$ | $2/16 = 1/8$ | decreasing | root | $\Theta(n^2)$ |
> | $D$ | $3/\sqrt3 = \sqrt3$ | increasing | leaves, $3^{\log_3 n} = n$ | $\Theta(n)$ |
> | $E$ | $3/3 = 1$ | all $n$ | all $\log_3 n$ levels | $\Theta(n \log n)$ |
> | $F$ | $3/9 = 1/3$ | decreasing | root | $\Theta(n^2)$ |
> | $G$ | $4/\sqrt2 = 2\sqrt2$ | increasing | leaves, $4^{\log_2 n} = n^2$ | $\Theta(n^2)$ |
> | $H$ | $4/2 = 2$ | increasing | leaves, $n^2$ | $\Theta(n^2)$ |
> | $I$ | $4/4 = 1$ | all $n^2$ | all $\log_2 n$ levels | $\Theta(n^2 \log n)$ |
>
> **Answer.** $A = \Theta(\sqrt n \log n)$, $B = \Theta(n)$, $C = \Theta(n^2)$, $D = \Theta(n)$, $E = \Theta(n \log n)$, $F = \Theta(n^2)$, $G = \Theta(n^2)$, $H = \Theta(n^2)$, $I = \Theta(n^2 \log n)$.

## Exercise 1.7 — Unbalanced recursion trees

> [!question] Exercise 1.7 (book p. 49)
> Use recursion trees to solve each of the following recurrences.
>
> **(j)** $J(n) = J(n/2) + J(n/3) + J(n/6) + n$
>
> **(k)** $K(n) = K(n/2) + 2K(n/3) + 3K(n/4) + n^2$
>
> **(l)** $L(n) = L(n/15) + L(n/10) + 2L(n/6) + \sqrt n$

### (j) Sizes that add up

> [!hint]- Hint
> $1/2 + 1/3 + 1/6 = 1$. Bound the level sums, the depth of the shallowest leaf and the depth of the deepest leaf.

> [!solution]- Solution
> A node of size $m$ has children of sizes $m/2$, $m/3$, $m/6$, which add up to $m$. So every full level sums to exactly $n$ and every level to at most $n$ (the leaves, of size between $1/6$ and $1$, number at most $6n$). The shallowest leaf, always dividing by 6, is at depth $\log_6 n$; the deepest, always dividing by 2, at depth $\log_2 n$. Hence
> $$
> n \log_6 n \;\le\; J(n) \;\le\; n(\log_2 n + 1) + O(n).
> $$
> As in the book's $T(n/3) + T(2n/3) + n$ example, the imbalance costs only a constant factor.
>
> **Answer.** $J(n) = \Theta(n \log n)$.

### (k) Decreasing levels

> [!hint]- Hint
> Compare the total cost of a node's children with the node's own cost.

> [!solution]- Solution
> A node of size $m$ costs $m^2$; its children cost
> $$
> \Big(\frac m2\Big)^2 + 2\Big(\frac m3\Big)^2 + 3\Big(\frac m4\Big)^2 = \Big(\frac14 + \frac29 + \frac3{16}\Big) m^2 = \frac{95}{144}\, m^2 .
> $$
> So level $i$ sums to at most $(95/144)^i n^2$ — a decreasing geometric series, dominated by the root: $n^2 \le K(n) \le n^2 / (1 - 95/144) = \frac{144}{49} n^2$ (plus lower-order leaf terms).
>
> **Answer.** $K(n) = \Theta(n^2)$.

### (l) Increasing levels, unbalanced tree

> [!hint]- Hint
> The level sums grow by the factor $1/\sqrt{15} + 1/\sqrt{10} + 2/\sqrt6 \approx 1.39$, so the leaves dominate. Because the tree is unbalanced, count the leaves with the exponent $\rho$ for which $15^{-\rho} + 10^{-\rho} + 2 \cdot 6^{-\rho} = 1$.

> [!solution]- Solution
> A node of size $m$ costs $\sqrt m$ and its children cost $r\sqrt m$ with $r = 1/\sqrt{15} + 1/\sqrt{10} + 2/\sqrt6 \approx 1.391 > 1$: the level sums increase, so the leaves dominate. The tree is unbalanced (leaves at depths from $\log_{15} n$ to $\log_6 n$), so "$r^{\text{depth}}$" does not count them. Instead give a node of size $m$ the weight $m^\rho$, where $\rho$ solves
> $$
> \Big(\frac1{15}\Big)^\rho + \Big(\frac1{10}\Big)^\rho + 2\Big(\frac16\Big)^\rho = 1, \qquad \rho \approx 0.6596 .
> $$
> The left side decreases in $\rho$ and is $r > 1$ at $\rho = 1/2$ and $1/2$ at $\rho = 1$, so $1/2 < \rho < 1$. Each node's weight equals the total weight of its children, so the leaves, which have constant size, number $\Theta(n^\rho)$. To show the internal nodes add nothing more, verify $L(n) = \Theta(n^\rho)$ by induction (substitution):
> - *Lower bound.* Try $L(n) \ge c\,n^\rho$. The recurrence gives $L(n) \ge c(n/15)^\rho + c(n/10)^\rho + 2c(n/6)^\rho = c\,n^\rho$, by the choice of $\rho$.
> - *Upper bound.* Try $L(n) \le c\,n^\rho - d\sqrt n$ with $d = 1/(r-1)$. The recurrence gives $L(n) \le c\,n^\rho - d r\sqrt n + \sqrt n = c\,n^\rho - d\sqrt n$, because $dr - 1 = d$.
>
> Both hold for the base cases by choosing $c$ small enough (lower bound) or large enough (upper bound).
>
> **Answer.** $L(n) = \Theta(n^\rho)$ with $\rho \approx 0.6596$ the root of $15^{-\rho} + 10^{-\rho} + 2\cdot 6^{-\rho} = 1$ — about $\Theta(n^{0.66})$.

## Exercise 1.8 — Logarithms and square roots

> [!question] Exercise 1.8 (book p. 49, marked ♥)
> Use recursion trees to solve each of the following recurrences.
>
> **(m)** $M(n) = 2M(n/2) + O(n \log n)$
>
> **(n)** $N(n) = 2N(n/2) + O(n/\log n)$
>
> **(p)** $P(n) = \sqrt n\, P(\sqrt n) + n$
>
> **(q)** $Q(n) = \sqrt{2n}\, Q(\sqrt{2n}) + \sqrt n$

### (m) n log n per node

> [!hint]- Hint
> The level sums are not geometric: level $i$ sums to $n(\lg n - i)$.

> [!solution]- Solution
> Take the additive term to be $n \lg n$ (an $O(n \log n)$ term is at most a constant times that). Level $i$ has $2^i$ nodes of size $n/2^i$, so it sums to $n \lg(n/2^i) = n(\lg n - i)$. Summing over $i = 0, \dots, \lg n - 1$:
> $$
> M(n) = n \sum_{j=1}^{\lg n} j + O(n) = \frac{n \lg n\,(\lg n + 1)}{2} + O(n) = \Theta(n \log^2 n).
> $$
> Exactly, with $M(1) = 1$ and $n$ a power of 2, $M(n) = n\big(1 + \lg n (\lg n + 1)/2\big)$.
>
> **Answer.** $M(n) = O(n \log^2 n)$ — and $\Theta(n \log^2 n)$ when the additive term is $\Theta(n \log n)$.

### (n) n over log n per node

> [!hint]- Hint
> Level $i$ sums to $n/(\lg n - i)$: a harmonic series.

> [!solution]- Solution
> Take the additive term to be $n/\lg n$. Level $i$ sums to $2^i \cdot \frac{n/2^i}{\lg(n/2^i)} = \frac{n}{\lg n - i}$ for $i = 0, \dots, \lg n - 1$ (nodes of size at least 2), so
> $$
> N(n) = n \sum_{j=1}^{\lg n} \frac1j + O(n) = n\, H_{\lg n} + O(n) = \Theta(n \log\log n),
> $$
> since the harmonic number $H_k = \ln k + O(1)$. Exactly, with $N(1) = 1$ and $n$ a power of 2, $N(n) = n(1 + H_{\lg n})$.
>
> **Answer.** $N(n) = O(n \log\log n)$ — and $\Theta(n \log\log n)$ when the additive term is $\Theta(n/\log n)$.

### (p) Square-root branching

> [!hint]- Hint
> A node of size $m$ has $\sqrt m$ children of size $\sqrt m$. What does a whole level sum to, and how many times can you take a square root before reaching 2?

> [!solution]- Solution
> The sizes never reach 1 by square roots, so use the base case $P(n) = \Theta(1)$ for $n \le 2$. Level $i$ has $n^{1/2 + 1/4 + \dots + 1/2^i} = n^{1 - 1/2^i}$ nodes of size $n^{1/2^i}$, so every level sums to exactly $n$. The size drops to at most 2 when $n^{1/2^i} \le 2$, that is, after $\lg\lg n$ levels; the last level has about $n/2$ leaves. So
> $$
> P(n) = n \lg\lg n + O(n) = \Theta(n \log\log n).
> $$
> Exactly, with $P(2) = 1$: $P(n)/n = P(\sqrt n)/\sqrt n + 1$, so $P(n) = n(\lg\lg n + 1/2)$ when $n = 2^{2^k}$.
>
> **Answer.** $P(n) = \Theta(n \log\log n)$.

### (q) Square roots that stall at 2

> [!hint]- Hint
> The sizes $n_{k+1} = \sqrt{2 n_k}$ decrease toward 2 and never pass it. Show that level $k$ has $2^k n / n_k$ nodes; the level sums then double each level.

> [!solution]- Solution
> Write $n_0 = n$ and $n_{k+1} = \sqrt{2n_k}$ for the node size on level $k$; then $n_k/2 = (n/2)^{1/2^k}$, which decreases toward 1, so $n_k \downarrow 2$ and never gets below 2. Use the base case $Q(n) = \Theta(1)$ for $n \le 4$.
>
> **Nodes per level.** Level $k$ has $N_k = n_1 n_2 \cdots n_k$ nodes. Multiplying $n_j^2 = 2 n_{j-1}$ for $j = 1..k$ gives $N_k^2 = 2^k\, n_0 \cdots n_{k-1}$, so $N_k = 2^k n / n_k$.
>
> **Level sums.** Level $k$ sums to $N_k \sqrt{n_k} = 2^k n / \sqrt{n_k}$. Since $n_{k+1} \le n_k$ (because $n_k \ge 2$), each level is at least twice the previous one: increasing, so the last level dominates.
>
> **Leaves.** The recursion stops at the first $L$ with $n_L \le 4$, that is, $(n/2)^{1/2^L} \le 2$, so $L = \lceil \lg\lg(n/2) \rceil$ and $\lg(n/2) \le 2^L < 2\lg(n/2)$. There are $N_L = 2^L n / n_L$ leaves with $2 < n_L \le 4$: $\Theta(n \log n)$ of them, each costing $\Theta(1)$, and they dominate.
>
> **Answer.** $Q(n) = \Theta(n \log n)$.

## Exercise 1.9 — Pancake sorting

> [!question] Exercise 1.9 (book pp. 49–50)
> A stack of $n$ pancakes of different sizes is to be sorted, smallest on top. The only operation is a **flip**: insert a spatula under the top $k$ pancakes, for some $1 \le k \le n$, and turn them over as a block.
>
> **(a)** Describe an algorithm that sorts any stack with $O(n)$ flips. Exactly how many flips does it perform in the worst case?
>
> **(b)** For every positive integer $n$, describe a stack of $n$ pancakes that requires $\Omega(n)$ flips to sort.
>
> **(c)** Now one side of each pancake is burned. Describe an algorithm that sorts any stack so that every burned side faces down, using $O(n)$ flips. Exactly how many flips does it perform in the worst case?

Stacks are written top to bottom; "flip $k$" reverses the top $k$ pancakes.

### (a) Two flips per pancake

> [!hint]- Hint
> Bring the largest pancake to the top, then flip it to the bottom; it never needs to move again.

> [!solution]- Solution
> **What the recursion solves.** $\textsf{PancakeSort}(k)$ sorts the top $k$ pancakes, assuming the pancakes below them are larger and already sorted. The answer is $\textsf{PancakeSort}(n)$.
>
> **Base case.** $k \le 1$: nothing to do.
>
> **Recursive case.** Let $p$ be the position of the largest of the top $k$ pancakes. If $p < k$: unless $p = 1$, flip $p$ (it comes to the top); then flip $k$ (it goes to position $k$). The pancakes below position $k$ are untouched. Then $\textsf{PancakeSort}(k-1)$.
>
> **Count.** At most 2 flips for each $k \ge 3$, and at most 1 for $k = 2$ (the larger of two is either at position 2 or on top), so at most
> $$
> F(n) = 2(n-2) + 1 = 2n - 3 \qquad (n \ge 2);
> $$
> one pancake needs no flip.
>
> **The bound is attained** for every $n \ge 2$: let $W_2 = 2\,1$ and let $W_n$ be $W_{n-1}$ reversed with $n$ inserted in the second position — $2\,1$, $1\,3\,2$, $2\,4\,3\,1$, $1\,5\,3\,4\,2$, … The largest pancake is in position 2, so the algorithm flips 2 and then $n$, which turns $W_n$ into $W_{n-1}$ on top of pancake $n$. By induction it uses $2(n-2)$ flips to reach $W_2$ and one more to finish.
>
> **Answer.** Flip the largest unsorted pancake to the top and then into place; $2n-3$ flips in the worst case (for $n \ge 2$).

### (b) A stack that needs n flips

> [!hint]- Hint
> Count the places where two neighboring pancakes have consecutive sizes, counting the plate as pancake $n+1$. How much can one flip change that count?

> [!solution]- Solution
> Number the pancakes $1..n$ by size and treat the plate as pancake $n+1$ under the stack. An **adjacency** is a pair of neighbors in the stack (including the bottom pancake and the plate) whose sizes differ by exactly 1. A sorted stack has $n$ adjacencies.
>
> **One flip creates at most one adjacency.** Flipping the top $k$ reverses them, so every neighboring pair inside the top $k$ stays a neighboring pair, and pairs below position $k$ are untouched. Only the pair at the cut changes: (pancake $k$, pancake $k+1$) becomes (old top, pancake $k+1$). Hence a stack with $a$ adjacencies needs at least $n - a$ flips.
>
> **A stack with no adjacencies** ($n \ge 4$): from top to bottom, the sizes with the same parity as $n$ in increasing order, then the other sizes in increasing order — for example $2\,4\,1\,3$ for $n = 4$ and $1\,3\,5\,2\,4$ for $n = 5$. Neighbors inside each block differ by 2; at the junction, $n$ sits above 1 or 2 (difference at least 2 when $n \ge 4$); and the bottom pancake $n-1$ sits on the plate $n+1$. So this stack needs at least $n$ flips. (Small $n$ do not matter for an asymptotic bound.)
>
> **Answer.** For $n \ge 4$, the same-parity-as-$n$ sizes in order followed by the other sizes in order: it has no adjacencies, each flip creates at most one, so it needs at least $n$ flips.

### (c) Burned pancakes

> [!hint]- Hint
> A flip turns every flipped pancake over. Arrange for the largest pancake to be burned side **up** when it is on top, just before you flip it into place.

> [!solution]- Solution
> **What the recursion solves.** $\textsf{BurnedSort}(k)$ sorts the top $k$ pancakes with every burned side down, assuming the pancakes below them are larger, sorted and burned side down. The answer is $\textsf{BurnedSort}(n)$.
>
> **Base case.** $k = 0$: nothing to do.
>
> **Recursive case.** Let $p$ be the position of the largest of the top $k$. If $p = k$ and its burned side is down, do nothing. Otherwise: unless $p = 1$, flip $p$ (it comes to the top); if its burned side is now down, flip 1; then flip $k$. A flip turns pancakes over, so the pancake that was on top, burned side up, lands in position $k$ burned side down. Then $\textsf{BurnedSort}(k-1)$.
>
> **Count.** At most 3 flips for each $k \ge 2$ and at most 1 for $k = 1$:
> $$
> 3(n-1) + 1 = 3n - 2 .
> $$
> **Attained** by the sorted stack with every burned side up: in each round the largest pancake is at position $k$, burned side up, so the round takes flip $k$, flip 1, flip $k$ — and the flips restore the top $k-1$ pancakes to sorted order, burned sides up. The last pancake takes one flip.
>
> **Answer.** Bring the largest pancake to the top, turn it burned side up if necessary, flip it into place; $3n - 2$ flips in the worst case.

## Exercise 1.10 — Median-of-three quicksort

> [!question] Exercise 1.10 (book p. 50)
> The median-of-three heuristic uses the median of the first, last and middle elements of the array as the quicksort pivot ([[2-algorithms/01-recursion#15-quicksort|§1.5]]). Prove that median-of-three quicksort needs $\Omega(n^2)$ time in the worst case: for every $n$, describe a permutation of $1, \dots, n$ on which the pivot of every recursive call is the second smallest element of its subarray.
>
> **(a)** Warm-up: assume Partition is *stable* — it keeps the elements smaller than the pivot in their existing order, and likewise the elements larger than the pivot. (The book writes "smaller" both times; the second is meant to be "larger".)
>
> (b) *Skipped (♥).* The same for the book's (unstable) Partition.

### (a) Stable partition

> [!hint]- Hint
> Put 1 first and 2 in the middle. After a stable partition, what is left of the array must have the same shape, two sizes smaller.

> [!solution]- Solution
> Fix the convention: on a subarray of $n$ elements, the heuristic looks at positions $1$, $\lceil n/2 \rceil$ and $n$. Let $q = \lceil n/2 \rceil - 1$ and take
> $$
> P_n = 1, 3, 5, \dots, 2q-1,\ \ 2, 4, \dots, 2q,\ \ 2q+1, \dots, n,
> $$
> the first $q$ odd numbers, then the first $q$ even numbers, then the rest in order. For example, $P_9 = 1, 3, 5, 7, 2, 4, 6, 8, 9$ and $P_{10} = 1, 3, 5, 7, 2, 4, 6, 8, 9, 10$.
>
> **Claim.** On $P_n$ (or on $P_n$ plus a constant), every recursive call on at least 3 elements uses the second smallest element as pivot. *Proof by induction on $n$.* For $n \ge 3$, position 1 holds 1, position $\lceil n/2 \rceil = q+1$ holds 2, and position $n$ holds $n \ge 3$; their median is 2. The stable partition leaves 1 alone on the left (a base case) and on the right
> $$
> 3, 5, \dots, 2q-1,\ \ 4, 6, \dots, 2q,\ \ 2q+1, \dots, n,
> $$
> which is $P_{n-2}$ plus 2, since $\lceil (n-2)/2 \rceil - 1 = q - 1$. The induction hypothesis covers it. Calls on one or two elements take constant time and do not matter. $\blacksquare$
>
> **Time.** Each call partitions in $\Theta(n)$ time and passes on $n - 2$ elements:
> $$
> T(n) = T(n-2) + T(1) + \Theta(n) = \Theta(n^2);
> $$
> Partition alone makes $(n-1) + (n-3) + \dots = \lfloor n^2/4 \rfloor$ comparisons. Any other choice of middle position works the same way: put 1 first, 2 in the middle position, and the permutation for $n - 2$ (plus 2) in the remaining positions.
>
> **Answer.** $1, 3, \dots, 2q-1, 2, 4, \dots, 2q, 2q+1, \dots, n$ with $q = \lceil n/2 \rceil - 1$: every pivot is the second smallest, each level removes only two elements, and the running time is $\Theta(n^2)$.

## Exercise 1.11 — StoogeSort

> [!question] Exercise 1.11 (book p. 50)
> ```text
> StoogeSort(A[0 .. n − 1]):
>   if n = 2 and A[0] > A[1]
>     swap A[0] ↔ A[1]
>   else if n > 2
>     m ← ⌈2n/3⌉
>     StoogeSort(A[0 .. m − 1])
>     StoogeSort(A[n − m .. n − 1])
>     StoogeSort(A[0 .. m − 1])
> ```
> **(a)** Prove that StoogeSort sorts its input.
>
> **(b)** Would it still sort correctly with $m = \lfloor 2n/3 \rfloor$ instead of $\lceil 2n/3 \rceil$? Justify your answer.
>
> **(c)** State a recurrence, with base cases, for the number of comparisons StoogeSort makes.
>
> **(d)** Solve the recurrence and prove the solution correct. [Hint: ignore the ceiling.]
>
> **(e)** Prove that StoogeSort makes at most $\binom n2$ swaps.

### (a) It sorts

> [!hint]- Hint
> Follow the $\lfloor n/3 \rfloor$ largest elements. After the first call, where can they be?

> [!solution]- Solution
> Strong induction on $n$. For $n \le 1$ there is nothing to sort, and for $n = 2$ one compare-and-swap sorts. Let $n \ge 3$, $m = \lceil 2n/3 \rceil$ (so $m < n$, and the recursive calls sort by the induction hypothesis) and $k = n - m$. Call the $k$ largest elements of $A$ **big** (with repeated values, read "the $k$ largest" as a multiset; nothing changes).
> - After the first call sorts $A[0..m-1]$, the big elements in that part are among its $k$ largest, so they sit in positions $m-k, \dots, m-1$.
> - Since $3m \ge 2n$, we have $m - k = 2m - n \ge n - m$: those positions lie inside $A[n-m..n-1]$. The other big elements were in $A[m..n-1]$ from the start. So all $k$ big elements are now in $A[n-m..n-1]$, and the second call puts them, sorted, into the last $k$ positions $A[m..n-1]$.
> - The third call sorts $A[0..m-1]$, which holds the other $n - k$ elements, none larger than a big one. Now both parts are sorted and everything in the first is at most everything in the second, so $A$ is sorted. $\blacksquare$
>
> **Answer.** The first two calls carry the $\lfloor n/3 \rfloor$ largest elements into the last third, in order — the ceiling guarantees the overlap $2m - n$ is at least $n - m$ — and the third call sorts the rest.

### (b) Floor instead of ceiling

> [!hint]- Hint
> Try $n = 4$.

> [!solution]- Solution
> **No.** For $n = 4$, $m = \lfloor 8/3 \rfloor = 2$, so the three calls sort $A[0..1]$, $A[2..3]$, $A[0..1]$; the two halves never interact. On $3\,4\,1\,2$ nothing moves at all, and the output $3\,4\,1\,2$ is not sorted. (The proof of (a) breaks exactly here: the overlap $2m - n = 0$ is smaller than $n - m = 2$.)
>
> **Answer.** No — the floor version leaves $3\,4\,1\,2$ unchanged.

### (c) The recurrence

> [!hint]- Hint
> Only calls on two elements compare array elements.

> [!solution]- Solution
> A call on $n > 2$ elements compares nothing itself and makes three calls on $\lceil 2n/3 \rceil$ elements; a call on two elements makes one comparison:
> $$
> C(0) = C(1) = 0, \qquad C(2) = 1, \qquad C(n) = 3\,C(\lceil 2n/3 \rceil) \quad (n \ge 3).
> $$
>
> **Answer.** $C(n) = 3C(\lceil 2n/3 \rceil)$ for $n \ge 3$, with $C(2) = 1$ and $C(0) = C(1) = 0$.

### (d) Solving it

> [!hint]- Hint
> Only the leaves of the recursion tree cost anything. Let $\alpha = \log_{3/2} 3$, so that $(2/3)^\alpha = 1/3$.

> [!solution]- Solution
> Ignoring the ceiling, the recursion tree has $3^i$ nodes at depth $i$ and only the leaves (size 2) cost anything; the depth is $\log_{3/2}(n/2)$, so
> $$
> C(n) = 3^{\log_{3/2}(n/2)} = (n/2)^{\log_{3/2} 3} = \Theta\big(n^{\log_{3/2} 3}\big) \approx \Theta(n^{2.71}).
> $$
> **Proof.** Treat $C$ as a function on the reals: $C(x) = 1$ for $4/3 < x \le 2$ and $C(x) = 3C(2x/3)$ for $x > 2$. Let $\alpha = \log_{3/2} 3$, so $(2/3)^\alpha = 1/3$. We claim $(x/2)^\alpha \le C(x) < 3(x/2)^\alpha$ for all $x > 4/3$. In the base range, $(x/2)^\alpha \in (1/3, 1]$, and $C(x) = 1$. For $x > 2$, by induction on the number of steps to the base range, $C(x) = 3C(2x/3)$ lies between $3(x/3)^\alpha$ and $9(x/3)^\alpha$, and $3(x/3)^\alpha = 3(2/3)^\alpha (x/2)^\alpha = (x/2)^\alpha$. $\blacksquare$
>
> With the ceiling the answer is the same; for instance, $C(n)/n^\alpha$ stays between $0.15$ and $0.81$ for all $2 \le n \le 200{,}000$.
>
> **Answer.** $C(n) = \Theta(n^{\log_{3/2} 3}) \approx \Theta(n^{2.71})$ — worse than insertion sort.

### (e) At most n choose 2 swaps

> [!hint]- Hint
> Every swap exchanges two *adjacent* elements of the original array.

> [!solution]- Solution
> Every recursive call works on a contiguous subarray, and swaps happen only in calls on two elements, so every swap exchanges two adjacent positions holding an inverted pair ($A[i] > A[i+1]$). Swapping an adjacent inverted pair removes exactly that one inversion and changes no other pair's order. So the number of inversions drops by exactly 1 per swap and never increases; it starts at most $\binom n2$ and ends at 0. In fact the number of swaps *equals* the number of inversions of the input.
>
> **Answer.** Swaps = inversions of the input $\le \binom n2$.

## Exercise 1.12 — Cruel and Unusual

> [!question] Exercise 1.12 (book pp. 50–51)
> Gary Miller's sorting algorithm, for $n$ a power of 2:
> ```text
> Cruel(A[1 .. n]):
>   if n > 1
>     Cruel(A[1 .. n/2])
>     Cruel(A[n/2 + 1 .. n])
>     Unusual(A[1 .. n])
>
> Unusual(A[1 .. n]):
>   if n = 2
>     if A[1] > A[2]                       ⟨⟨the only comparison!⟩⟩
>       swap A[1] ↔ A[2]
>   else
>     for i ← 1 to n/4                     ⟨⟨swap 2nd and 3rd quarters⟩⟩
>       swap A[i + n/4] ↔ A[i + n/2]
>     Unusual(A[1 .. n/2])                 ⟨⟨recurse on left half⟩⟩
>     Unusual(A[n/2 + 1 .. n])             ⟨⟨recurse on right half⟩⟩
>     Unusual(A[n/4 + 1 .. 3n/4])          ⟨⟨recurse on middle half⟩⟩
> ```
> (a) *Skipped.* Prove by induction that Cruel sorts every input.
>
> **(b)** Prove that Cruel would not sort correctly if the for-loop were removed from Unusual.
>
> **(c)** Prove that Cruel would not sort correctly if the last two lines of Unusual were swapped.
>
> **(d)** What is the running time of Unusual? **(e)** What is the running time of Cruel? Justify your answers.

### (b) Without the quarter swap

> [!hint]- Hint
> A counterexample is a proof. Try $n = 4$ with two sorted halves.

> [!solution]- Solution
> Take $A = 3\,4\,1\,2$. Cruel first sorts the halves $3\,4$ and $1\,2$, which are already sorted, and calls Unusual on $3\,4\,1\,2$. Without the loop, Unusual compares $A[1]$ with $A[2]$ ($3 < 4$), then $A[3]$ with $A[4]$ ($1 < 2$), then $A[2]$ with $A[3]$ ($4 > 1$, swap). The result $3\,1\,4\,2$ is not sorted.
>
> **Answer.** Cruel turns $3\,4\,1\,2$ into $3\,1\,4\,2$.

### (c) Middle before right

> [!hint]- Hint
> The same input works.

> [!solution]- Solution
> On $A = 3\,4\,1\,2$, Cruel again reaches Unusual on $3\,4\,1\,2$. The loop swaps $A[2] \leftrightarrow A[3]$: $3\,1\,4\,2$. Left half: $3 > 1$, swap: $1\,3\,4\,2$. Middle half (positions 2, 3): $3 < 4$. Right half (positions 3, 4): $4 > 2$, swap: $1\,3\,2\,4$ — not sorted.
>
> **Answer.** With the last two lines swapped, Cruel turns $3\,4\,1\,2$ into $1\,3\,2\,4$.

### (d) Running time of Unusual

> [!hint]- Hint
> Three half-size calls plus a linear loop.

> [!solution]- Solution
> Unusual on $n$ elements does $n/4$ swaps and three calls on $n/2$ elements:
> $$
> U(2) = \Theta(1), \qquad U(n) = 3U(n/2) + \Theta(n).
> $$
> The level sums $\Theta(n)(3/2)^i$ increase, so the $3^{\lg n - 1} = n^{\lg 3}/3$ leaves dominate. (Exactly $n^{\lg 3}/3$ comparisons.)
>
> **Answer.** $U(n) = \Theta(n^{\lg 3}) \approx \Theta(n^{1.585})$.

### (e) Running time of Cruel

> [!hint]- Hint
> Two half-size calls plus one Unusual.

> [!solution]- Solution
> $$
> C(1) = \Theta(1), \qquad C(n) = 2C(n/2) + \Theta(n^{\lg 3}).
> $$
> Level $i$ sums to $2^i (n/2^i)^{\lg 3} = n^{\lg 3}(2/3)^i$: decreasing, so the root dominates. (Exactly $n^{\lg 3} - n$ comparisons.)
>
> **Answer.** $C(n) = \Theta(n^{\lg 3}) \approx \Theta(n^{1.585})$ — Cruel is as fast as its last Unusual.

## Exercise 1.13 — Counting inversions

> [!question] Exercise 1.13 (book p. 51)
> An **inversion** in an array $A[1..n]$ is a pair of indices $(i, j)$ with $i < j$ and $A[i] > A[j]$; an array has between 0 (sorted) and $\binom n2$ (sorted backward) inversions. Describe and analyze an algorithm that counts the inversions of an $n$-element array in $O(n \log n)$ time. [Hint: modify mergesort.]

> [!hint]- Hint
> Inversions inside each half are counted recursively. An inversion across the halves is a left element larger than a right element: count them while merging, at the moment a right element is copied.

> [!solution]- Solution
> **What the recursion solves.** $\textsf{CountInversions}(A[1..n])$ sorts $A$ *and* returns the number of inversions $A$ had. (Returning the sorted array is the generalization that makes the merge step possible.) It follows mergesort ([[2-algorithms/01-recursion#14-mergesort|§1.4]], [[concepts/divide-and-conquer]]):
> ```text
> CountInversions(A[1 .. n]):
>   if n ≤ 1
>     return 0
>   m ← ⌊n/2⌋
>   x ← CountInversions(A[1 .. m])
>   y ← CountInversions(A[m + 1 .. n])
>   return x + y + MergeCount(A[1 .. n], m)
>
> MergeCount(A[1 .. n], m):        ⟨⟨A[1 .. m], A[m + 1 .. n] sorted⟩⟩
>   i ← 1;  j ← m + 1;  c ← 0
>   for k ← 1 to n
>     if j > n or (i ≤ m and A[i] ≤ A[j])
>       B[k] ← A[i];  i ← i + 1
>     else
>       B[k] ← A[j];  j ← j + 1
>       c ← c + (m − i + 1)          ⟨⟨A[i .. m] are all > A[j]⟩⟩
>   copy B[1 .. n] into A[1 .. n]
>   return c
> ```
> **Base case.** An array of at most one element has no inversion.
>
> **Recursive calls.** Every inversion $(i, j)$ has both indices in the left half, both in the right half, or $i \le m < j$. The two calls count the first two kinds. Sorting each half permutes elements only within the halves, so it does not change the set of cross pairs or how many of them are inverted.
>
> **Combination.** When $\textsf{MergeCount}$ copies a right element $A[j]$, the left elements not yet copied are $A[i..m]$, and all of them exceed $A[j]$ (ties go to the left first); the left elements already copied are at most $A[j]$. So each cross inversion is counted exactly once, when its right element is copied.
>
> **Time.** Merging takes $O(n)$ time:
> $$
> T(n) = T(\lceil n/2 \rceil) + T(\lfloor n/2 \rfloor) + O(n) = O(n \log n),
> $$
> since every level of the recursion tree sums to $O(n)$ and there are $O(\log n)$ levels ([[2-algorithms/01-recursion#17-recursion-trees|§1.7]]).
>
> **Answer.** Mergesort that also counts, during each merge, the remaining left elements every time it takes a right element: $O(n \log n)$ time.

### Sources for this page

Statements paraphrased from Exercises 1–13 of Chapter 1 of Jeff Erickson's *Algorithms* (pp. 44–51; CC BY 4.0), with the book's examples (the 21-move Baguenaudier sequence, Figure 1.17 of the Towers of Pisa, the code of RulerHanoi, StoogeSort, Cruel and Unusual). The solutions and the extra examples are original. Corrections to the book: the move direction in RulerHanoi (1.1(d)), the ambiguous rule in 1.1(b), the remark in 1.5(a), and "smaller … smaller" in 1.10(a). Everything is checked by `tools/checks/a01x.py`: the four non-recursive Hanoi algorithms are simulated against the recursive one for $n \le 12$ (and the printed RulerHanoi is shown to fail); every move sequence on the page is simulated, its legality checked and its moves counted; optimality claims are confirmed by breadth-first search over all positions; the recurrences are evaluated numerically, at exact powers and with floors, against their closed forms or bounds; and the sorting and counting algorithms are run against brute force on all small inputs.
