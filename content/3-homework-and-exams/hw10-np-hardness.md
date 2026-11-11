---
title: "HW10 — NP, reductions and NP-hardness: study guide"
description: "Homework 10 (CS/ECE 374 A, Fall 2026, due Tuesday, November 17) is open, so this page is a study guide and not a write-up: what each problem asks and practices (membership in NP, a reduction to Sat and what it does not prove, an NP-hardness proof for a string problem), the rubric each part is graded by, what a complete answer contains, test instances to try your own answer on, and where the same kind of problem is already worked on this site. The handout's own solved problem, the red and blue stone puzzle, is explained in full."
tags: [homework, algorithms, complexity]
---

*Homework 10 · CS/ECE 374 A, Fall 2026 · due Tuesday, November 17, 2026, 9 pm · **open — no solutions to Problems 1 and 2 here** · the method: [[2-algorithms/12-np-hardness|Chapter 12]], [[concepts/polynomial-time-reductions|polynomial-time reductions]], [[concepts/np-hardness|NP-hardness]] · the rubric: [[0-toolkit/06-how-exams-are-graded#14-np-hardness|how exams are graded §14]] · the write-up template: [[0-toolkit/02-proof-templates#23-proving-a-problem-np-hard|proof templates §23]] · in class: [[5-lecture-log/2026-11-10|Tue Nov 10]] · the previous write-up: [[3-homework-and-exams/hw9-more-graph-algorithms|HW9]]*

> [!warning] An open homework: a study guide, not solutions
> Homework 10 is due on Tuesday, November 17, at 9 pm, and no official solutions have been posted. So this page does **not** solve Problems 1 and 2. For each part it says what is being asked, which technique and which rubric it calls for, what a complete answer has to contain, how to test your own answer, and where a problem of the same kind is worked out on this site. Problem 3 is different: the handout itself prints its solution as a model, and that solution is explained here in full.

> [!abstract] In one breath
> The homework has three jobs, one per problem. **Problem 1** takes a problem that is *easy* (perfect matching) through the vocabulary of the chapter: say why it is in NP, reduce it **to** Sat, and explain why an easy problem reducing to a hard one proves nothing about P and NP — the direction of a reduction is the whole point. **Problem 2** is a full NP-hardness proof, for a problem about strings over $\{\mathtt{0}, \mathtt{1}, \mathtt{2}\}$: choose a known NP-hard problem, reduce it **to** the new one, prove both directions, say "polynomial time". **Problem 3**, solved in the handout, is the model for how such a proof is written.

## What the homework practices

| problem | kind of question | what is graded | the same kind of problem on this site |
|---|---|---|---|
| 1(a) | membership in NP | a certificate and a polynomial-time check | [[2-algorithms/12-np-hardness#122-p-versus-np\|§12.2]] (CircuitSat is in NP) |
| 1(b) | a polynomial-time many-one reduction **to** Sat | the construction, both directions of "if and only if", polynomial time | [[2-algorithms/12-np-hardness-exercises#exercise-122--boxdepth\|Exercise 12.2(a)]] (an easy problem reduced to a hard one); [[concepts/cook-levin-theorem\|Cook–Levin]] (requirements written as clauses) |
| 1(c) | a conceptual question about the direction of reductions | a short, precise explanation | [[2-algorithms/12-np-hardness-exercises#exercise-122--boxdepth\|Exercise 12.2(c)]], [[2-algorithms/12-np-hardness-exercises#what-the-conceptual-exercises-teach\|what the conceptual exercises teach]] |
| 2 | an NP-hardness proof | the [[0-toolkit/06-how-exams-are-graded#14-np-hardness\|NP-hardness rubric]], 10 points | Problem 3 below; [[3-homework-and-exams/lab-12b\|Lab 12b]]; [[2-algorithms/12-np-hardness-exercises\|Chapter 12 exercises]] |
| 3 | an NP-hardness proof, solved in the handout | — | [[2-algorithms/12-np-hardness-exercises#exercise-1234--red-and-blue-stones\|Exercise 12.34]] |

## Problem 1 — Perfect matching: in NP, reducible to Sat, and still not a proof that P = NP

> [!question] Problem 1
> Let $G = (V, E)$ be an undirected graph. A **matching** in $G$ is a set $M\subseteq E$ of edges no two of which share a vertex. A matching is **perfect** if $2\lvert M\rvert = \lvert V\rvert$: every vertex is an endpoint of exactly one edge of $M$. The problem **PerfectMatching**: given an undirected graph $G$, does $G$ have a perfect matching?
>
> (a) Give a short argument that PerfectMatching is in NP.
>
> (b) Recall that the input to **Sat** is a boolean formula in conjunctive normal form — an And of one or more clauses, each the Or of one or more literals, each a variable or its negation; clauses need not have any particular number of literals — and that Sat asks whether the formula has a satisfying assignment. Describe a polynomial-time many-one reduction **from PerfectMatching to Sat**: a polynomial-time algorithm that transforms an instance $G$ of PerfectMatching into an instance $\Phi$ of Sat such that $G$ has a perfect matching if and only if $\Phi$ is satisfiable. Describe it yourself — do not merely appeal to the Cook–Levin theorem — and prove that it is correct.
>
> (c) There is a polynomial-time algorithm for PerfectMatching (beyond the scope of the course). Why does that algorithm, together with the result of (b), not imply P = NP?

### (a) What "in NP" asks for

A decision problem is in NP if every YES instance has a **certificate** — a short proof that the answer is yes — that can be **checked in polynomial time** ([[2-algorithms/12-np-hardness#122-p-versus-np|§12.2]]). A complete answer is two or three sentences and names two things: what the certificate is, and how it is checked and how long the check takes. Nothing has to be said about *finding* the certificate, and nothing about NO instances. The grading rubric gives membership in NP one point, for describing the certificate; Lab 12b's handout adds that for a problem of the form "is there a foo in this input?", the certificate is usually that foo.

On this site: the paragraph "CircuitSat is in NP" in [[2-algorithms/12-np-hardness#122-p-versus-np|§12.2]] is an answer of exactly this shape, and its table lists the certificate for each class.

### (b) What a reduction to Sat must contain

Read the direction twice: this is a reduction **from** PerfectMatching **to** Sat. It is not an NP-hardness proof of anything; it shows that Sat is at least as hard as PerfectMatching. It is graded like any many-one reduction ([[5-lecture-log/2026-11-10|lecture of Nov 10]]): an algorithm on an arbitrary instance, a proof in both directions, and a running time.

> [!recipe] A checklist for your answer
> 1. **The variables** of $\Phi$, as an explicit function of $G$, with one sentence saying what it means for each variable to be True.
> 2. **The clauses**, as an explicit function of $G$, each family tied to one requirement in the definition of a perfect matching. The handout stresses that a clause may have any number of literals — use that freedom.
> 3. **The size** of $\Phi$ in terms of $\lvert V\rvert$ and $\lvert E\rvert$, and the words **polynomial time**.
> 4. **⇒** Suppose $G$ has a perfect matching $M$. Define an assignment from $M$ and show that it satisfies every clause.
> 5. **⇐** Suppose an assignment satisfies $\Phi$. Define a set of edges from it and show that it is a perfect matching — both halves of the definition.
>
> The reduction must work for **every** graph, and it may not know whether $G$ has a perfect matching.

**Test your reduction** on small graphs whose answers are known. Build $\Phi$ by hand and check that it is satisfiable exactly for the YES instances:

| graph | perfect matchings | answer |
|---|---|---|
| a single edge | 1 | YES |
| a path on three vertices | 0 | NO |
| a triangle | 0 | NO |
| a 4-cycle | 2 | YES |
| a star with three leaves (four vertices) | 0 | NO |

A graph with an odd number of vertices never has a perfect matching, since a matching with $r$ edges covers exactly $2r$ vertices; the star shows that an even number of vertices is not enough. If your formula for the star or the triangle comes out satisfiable, a requirement of the definition is missing from your clauses.

On this site, constraints turned into clauses: the gate-by-gate clauses of [[2-algorithms/12-np-hardness#125-reductions-and-sat|§12.5]] and [[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]], and the tableau clauses of the Cook–Levin proof ([[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem|Models §9.6]], [[concepts/cook-levin-theorem]]) — which is the general theorem the handout tells you not to hide behind. A reduction from an easy problem to a hard one, written out with its proof, is [[2-algorithms/12-np-hardness-exercises#exercise-122--boxdepth|Exercise 12.2(a)]].

### (c) What the question is testing

It tests the **direction rule**: what exactly follows from "$A$ reduces to $B$" together with a fast algorithm for $A$, and what would be needed instead to conclude P = NP. A good answer is a few sentences that name the two problems, say which way the reduction of (b) goes, and say what a proof of P = NP would require. Chapter 12 has three exercises of this kind, solved on this site: [[2-algorithms/12-np-hardness-exercises#exercise-122--boxdepth|Exercise 12.2(c)]] (the closest parallel: an easy problem reduced to MaxClique), [[2-algorithms/12-np-hardness-exercises#exercise-121--partition-in-pseudo-polynomial-time|Exercise 12.1(b)]] and [[2-algorithms/12-np-hardness-exercises#exercise-124--allornothing3sat|Exercise 12.4(b)]]; the summary is [[2-algorithms/12-np-hardness-exercises#what-the-conceptual-exercises-teach|what the conceptual exercises teach]]. The lemma and its contrapositive are in [[5-lecture-log/2026-11-10|the lecture of Nov 10]] and in [[concepts/polynomial-time-reductions]].

## Problem 2 — StringMatch is NP-hard

> [!question] Problem 2
> Prove that the following problem, **StringMatch**, is NP-hard. The input is a finite set $S$ of strings, all of the same length $n$, over the alphabet $\{\mathtt{0}, \mathtt{1}, \mathtt{2}\}$. The question: is there a string $w\in\{\mathtt{0}, \mathtt{1}\}^n$ such that for every string $s\in S$, the strings $s$ and $w$ have the **same symbol in at least one position**?
>
> For example, for $S = \{\mathtt{01220}, \mathtt{21110}, \mathtt{21120}, \mathtt{00211}, \mathtt{11101}\}$ the answer is $\textsf{True}$: the string $w = \mathtt{01001}$ agrees with the first three strings of $S$ in the second position and with the last two in the last position. For $S = \{\mathtt{2002}, \mathtt{2112}, \mathtt{2012}, \mathtt{2102}\}$ the answer is $\textsf{False}$.

**What kind of problem this is.** A standard NP-hardness proof, graded by the [[0-toolkit/06-how-exams-are-graded#14-np-hardness|NP-hardness rubric]] (10 points):

| points | for |
|---|---|
| 1 | a reasonable known NP-hard problem $X$ to reduce from (the problem does not name one, so the choice is yours) |
| 2 | a structurally sound reduction: an algorithm that takes an **arbitrary instance of $X$** and nothing else, builds an instance of StringMatch, and runs in polynomial time — if this is wrong, nothing else earns credit |
| 2 | the reduction is correct: YES instances go to YES instances and NO to NO |
| 2 | the "only if" proof: a YES instance of $X$ becomes a YES instance of StringMatch |
| 2 | the "if" proof: if the set $S$ you built is a YES instance, the instance of $X$ was one |
| 1 | the words "polynomial time" (only if the reduction is correct) |

A reduction in the wrong direction — solving StringMatch with the help of the known problem — is worth at most 1 point.

**How to approach it** (the method, not the answer).

1. **Understand the problem on the examples.** In the first example, 23 of the 32 binary strings of length 5 work, $\mathtt{01001}$ among them. In the second, none of the 16 binary strings of length 4 works: the four strings of $S$ carry all four patterns $\mathtt{00}, \mathtt{11}, \mathtt{01}, \mathtt{10}$ in their middle positions. Work out by hand *why* each string of $S$ rules out some choices of $w$; that is where the reduction comes from.
2. **Name the certificate.** What object proves that an instance is a YES instance, and what does each string of $S$ demand of it? Then ask which known NP-hard problem has a certificate and constraints of the same shape.
3. **Choose the problem to reduce from** with the rules of thumb of [[2-algorithms/12-np-hardness#1214-choosing-the-right-problem|§12.14]]. Any NP-hard problem from the lecture notes is allowed.
4. **Write the reduction as an algorithm** on an arbitrary instance of that problem: what $n$ is, and each string of $S$, position by position. Count the strings and their length.
5. **Prove both directions** by translating certificates: from a certificate of the known problem to a string $w$, and from a string $w$ back.
6. **Use the template** [[0-toolkit/02-proof-templates#23-proving-a-problem-np-hard|§23]] so that no rubric item is missing.

**Problems of the same kind, worked on this site:** the handout's own Problem 3, below; the five reductions of [[3-homework-and-exams/lab-12b|Lab 12b]], all in the rubric's format; [[2-algorithms/12-np-hardness#127-maximum-independent-set-from-3sat|§12.7]] (3Sat to independent set) and [[2-algorithms/12-np-hardness#1212-subset-sum-from-vertex-cover|§12.12]] (vertex cover to subset sum) for the two styles of gadget; and [[2-algorithms/12-np-hardness-exercises#exercise-1226--dominating-set|Exercises 12.26]], [[2-algorithms/12-np-hardness-exercises#exercise-1234--red-and-blue-stones|12.34]] and [[2-algorithms/12-np-hardness-exercises#exercise-1238--three-way-teams|12.38]].

> [!trap] What loses the points
> - **The wrong direction.** The reduction's input is an instance of the *known* hard problem; its output is a set of strings.
> - **A reduction that handles only convenient instances**, or that uses the answer (it does not know whether its input is a YES instance).
> - **One direction only.** The "if" proof — a matching string $w$ gives back a certificate of the known problem — is the one that gets forgotten.
> - **No size count**, or no "polynomial time".

## Problem 3 — RedBlue, the handout's solved problem

> [!question] Problem 3 (solved in the handout)
> **RedBlue** is a puzzle on an $n\times m$ grid of squares, each empty, occupied by a red stone, or occupied by a blue stone. The goal is to remove some of the stones so that (1) every row contains at least one stone and (2) no column contains stones of both colors. For some puzzles this is impossible. Prove that it is NP-hard to determine whether a given RedBlue puzzle has a solution.

The handout prints this solution as the model for the two problems above; here it is, with the rubric items marked.

**The known problem (1 point).** 3Sat.

**The reduction (2 + 2 points).** Given an arbitrary 3CNF formula $\Phi$ with $m$ variables $x_1, \dots, x_m$ and $n$ clauses, build an $n\times m$ board: one **row per clause**, one **column per variable**. In square $(i, j)$ put a **blue** stone if $x_j$ appears in clause $i$, a **red** stone if $\bar x_j$ appears in clause $i$, and nothing otherwise. The board has $3n$ stones and is built in $O(nm)$ time.

**Why this is the right picture.** A column must end up with one color: keeping its blue stones says "$x_j$ is True", keeping its red stones says "$x_j$ is False". A row must keep a stone: the clause has a true literal. Condition (2) is "an assignment is consistent", condition (1) is "every clause is satisfied".

**⇒ (2 points).** Suppose $\Phi$ is satisfiable, and fix a satisfying assignment. In column $j$, remove the red stones if $x_j$ is True and the blue stones if $x_j$ is False — that is, remove exactly the stones of false literals. Each column keeps one color at most. Each clause has a true literal, whose stone was not removed, so each row keeps a stone. The puzzle is solvable.

**⇐ (2 points).** Suppose the puzzle is solvable, and fix a solution. Set $x_j$ to True if column $j$ still has blue stones, to False if it still has red stones, and arbitrarily if it is empty. Then every remaining stone stands for a true literal. Each row keeps a stone, so each clause has a true literal: $\Phi$ is satisfied.

**Polynomial time (1 point).** The handout closes with "This reduction clearly requires only polynomial time."

> [!note] Three remarks on the handout's solution
> - **A case it does not mention.** If a clause contains both $x_j$ and $\bar x_j$, square $(i, j)$ would need two stones. Such a clause is always true, so drop it before building the board; this site's write-up of the same problem starts with that step.
> - **Colors.** The handout uses blue for positive literals and red for negated ones; [[2-algorithms/12-np-hardness-exercises#exercise-1234--red-and-blue-stones|Exercise 12.34]] on this site uses red for positive. Nothing depends on it.
> - **"Clearly."** The model answer says "clearly requires only polynomial time". The rubric wants the words "polynomial time"; a size count ($3n$ stones on an $n\times m$ board) is the safer way to earn them.

## Before you hand it in

- Every reduction: **from** which problem **to** which? Say it in the first sentence.
- Does your algorithm accept an *arbitrary* instance, and use nothing but that instance?
- Two proofs, each starting from a certificate: "suppose … is a YES instance" in one direction, "suppose the instance we built is a YES instance" in the other.
- The size of what you build, and the words "polynomial time".
- For 1(a): the certificate and the check. For 1(c): the direction.

### Sources for this page
The CS/ECE 374 A (Fall 2026) Homework 10 handout: Problems 1 and 2 (statements paraphrased, with the handout's two examples) and the solved Problem 3 with its printed solution, explained in our own words; the rubric as paraphrased on [[0-toolkit/06-how-exams-are-graded#14-np-hardness|how exams are graded]]. The homework was open when this page was written (due November 17, no solutions posted), so Problems 1 and 2 are not solved here. Checked by `tools/checks/hw10.py`, which contains no solution either: the perfect matchings of the five test graphs and the parity fact by exhaustive search; the two StringMatch examples straight from the definition (23 of 32 strings work in the first, none of 16 in the second); and the handout's RedBlue reduction on 600 3CNF formulas against an exhaustive search of the puzzle, with both certificate translations of its proof and the uncovered case of a clause containing a variable and its negation.
