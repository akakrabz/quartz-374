---
title: "Lab 12b — Six variants of Sat"
description: "NP-hardness proofs in the rubric's format for five restricted or modified satisfiability problems — 4Sat (pad each clause with a new variable in both signs), BalancedSat (a mirror variable for every variable), Exact3Sat or one-in-three Sat (a three-clause gadget per clause), Sat with at most three literals per clause and three occurrences per variable (copies joined by a cycle of implications), and 3Sat with at most four occurrences per variable (a five-clause enforcer that pins a padding variable to False) — and a polynomial-time algorithm for XorSat, which is a system of linear equations modulo 2."
tags: [lab, algorithms, complexity]
---

*Lab 12b · November 13 · CS/ECE 374 A, Fall 2026 · NP-hardness by reduction from [[concepts/satisfiability|3Sat]] · uses [[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]], [[2-algorithms/12-np-hardness#128-the-general-pattern|§12.8]], [[2-algorithms/12-np-hardness#1213-other-useful-np-hard-problems|§12.13]] · rubric: [[0-toolkit/06-how-exams-are-graded#14-np-hardness|how exams are graded §14]] · template: [[0-toolkit/02-proof-templates#23-proving-a-problem-np-hard|proof templates §23]] · solutions: ours — no official solutions were posted*

> [!abstract] In one breath
> Five of the six problems ask for an NP-hardness proof of a variant of Sat, and all five are reductions **from** 3Sat (directly, or through an earlier problem of the lab) that work **one clause or one variable at a time**. **4Sat:** pad every clause with a new variable, once positive and once negated, so the padding cannot help. **BalancedSat:** give every variable a mirror variable forced to the opposite value, so every satisfying assignment is balanced. **Exact3Sat:** replace a clause $(a\vee b\vee c)$ by three clauses on four new variables that can have exactly one true literal each precisely when $a\vee b\vee c$ holds. **At most three occurrences:** replace the occurrences of a frequent variable by separate copies and tie the copies together with a cycle of implications. **Exactly three literals, at most four occurrences:** pad the short clauses of the previous problem with new variables that a five-clause *enforcer* pins to False. The sixth problem goes the other way: **XorSat** is easy, because an exclusive-or clause is a linear equation modulo 2 and Gaussian elimination solves the system.

> [!recipe] What an NP-hardness proof contains (the handout's first page)
> To prove that a decision problem $Y$ is NP-hard:
> 1. **Choose** a problem $X$ that is already known to be NP-hard.
> 2. **Reduce $X$ to $Y$:** describe an algorithm that turns an *arbitrary* instance $x$ of $X$ into an instance $y$ of $Y$. Think of it as solving $X$ with a magic box for $Y$.
> 3. **Prove both directions:** a YES instance of $X$ becomes a YES instance of $Y$; and if the instance of $Y$ you built is a YES instance, the instance of $X$ you started from was one. When both problems are in NP, each direction turns a certificate for one instance into a certificate for the other.
> 4. **Say that the reduction takes polynomial time.**
>
> For NP-*completeness* you also argue $Y\in\textsf{NP}$ by naming the polynomial-size certificate. The same list with its points is the [[0-toolkit/06-how-exams-are-graded#14-np-hardness|NP-hardness rubric]]; the boilerplate is [[0-toolkit/02-proof-templates#23-proving-a-problem-np-hard|template §23]].

**Conventions.** A **literal** is a variable $x$ or its negation $\bar x$. A CNF formula is an And of **clauses**, each an Or of literals; a clause is a set of *distinct* literals. **Sat** asks whether a CNF formula has a satisfying assignment; **3Sat** is the special case in which every clause has exactly three distinct literals; both are NP-hard ([[2-algorithms/12-np-hardness#125-reductions-and-sat|§12.5]], [[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]]). Below, $\Phi$ is the given formula, with $n$ variables and $k$ clauses, and $\Phi'$ is the formula the reduction builds.

## Problem 1 — 4Sat

> [!question] Problem 1
> **4Sat** is the special case of Sat in which every clause of the input formula contains exactly four distinct literals. Prove that 4Sat is NP-hard. *(Hint: reduce from 3Sat.)*

> [!hint]- Hint
> A fourth literal that is new could simply be set to True. Add it in a way that makes this useless.

> [!solution]- Solution
> **The idea.** A clause needs a fourth literal, and the only safe source is a new variable $z$. But $(a\vee b\vee c\vee z)$ alone is satisfied by $z = \textsf{True}$ whatever $a, b, c$ are. So add the clause twice, once with $z$ and once with $\bar z$: whichever value $z$ takes, one of the two copies gets no help from it.
>
> **Reduce from** 3Sat.
>
> **Reduction.** Given an arbitrary 3CNF formula $\Phi$ with clauses $C_1, \dots, C_k$, introduce one new variable $z_j$ per clause and replace each clause $C_j = (a\vee b\vee c)$ by the two clauses
>
> $$
> (a\vee b\vee c\vee z_j)\ \wedge\ (a\vee b\vee c\vee\bar z_j).
> $$
>
> The result $\Phi'$ has $n + k$ variables and $2k$ clauses, each with exactly four distinct literals ($z_j$ is new, so it differs from $a, b, c$). It is built in $O(k)$ time: **polynomial time**.
>
> **⇒** Suppose an assignment satisfies $\Phi$. Extend it by any values for the $z_j$. Every clause of $\Phi'$ contains a whole clause of $\Phi$, which has a true literal. So $\Phi'$ is satisfiable.
>
> **⇐** Suppose an assignment satisfies $\Phi'$, and fix a clause $C_j = (a\vee b\vee c)$ of $\Phi$. If $z_j$ is False, the clause $(a\vee b\vee c\vee z_j)$ is satisfied by one of $a, b, c$; if $z_j$ is True, the clause $(a\vee b\vee c\vee\bar z_j)$ is. Either way $C_j$ has a true literal. So the same assignment, restricted to the variables of $\Phi$, satisfies $\Phi$.
>
> **Answer.** $\Phi$ is satisfiable if and only if $\Phi'$ is, and $\Phi'$ is built in polynomial time; so 4Sat is NP-hard. (One new variable shared by all clauses works equally well.)

> [!trap] Two paddings that do not work
> - **Only one copy**, $(a\vee b\vee c\vee z_j)$: every formula built this way is satisfiable (set every $z_j$ to True), so unsatisfiable formulas are mapped to satisfiable ones — the "⇐" proof fails.
> - **Repeating a literal**, $(a\vee b\vee c\vee c)$: logically fine, but not four *distinct* literals, so it is not an instance of 4Sat.

The same padding, with nine new variables in all 512 sign patterns, is [[2-algorithms/12-np-hardness-exercises#exercise-127--twelve-is-as-hard-as-three|Exercise 12.7(c)]] (12Sat).

## Problem 2 — BalancedSat

> [!question] Problem 2
> **BalancedSat** asks whether a given CNF formula $\Phi$ has a satisfying assignment in which **exactly half of the variables are True**. Prove that BalancedSat is NP-hard.

> [!hint]- Hint
> You may add variables. Add them so that the count of True variables takes care of itself.

> [!solution]- Solution
> **The idea.** A satisfying assignment of $\Phi$ can have any number of true variables, and the reduction does not know that number. So make the count automatic: for every variable $x_i$ add a mirror variable $y_i$ that is forced to be the opposite of $x_i$. Then every pair $x_i, y_i$ contributes exactly one True, whatever the assignment.
>
> **Reduce from** Sat (the reduction never looks at the size of the clauses, so 3Sat works just as well).
>
> **Reduction.** Given an arbitrary CNF formula $\Phi$ with variables $x_1, \dots, x_n$, add new variables $y_1, \dots, y_n$ and the clauses
>
> $$
> (x_i\vee y_i)\ \wedge\ (\bar x_i\vee\bar y_i)\qquad\text{for } i = 1, \dots, n .
> $$
>
> The result $\Phi'$ has $2n$ variables and $k + 2n$ clauses, and is built in linear time: **polynomial time**.
>
> **⇒** Suppose an assignment satisfies $\Phi$. Set $y_i$ to the opposite of $x_i$ for every $i$. The clauses of $\Phi$ are still satisfied; $(x_i\vee y_i)$ and $(\bar x_i\vee\bar y_i)$ are satisfied because exactly one of $x_i, y_i$ is True. And exactly $n$ of the $2n$ variables are True. So $\Phi'$ has a balanced satisfying assignment.
>
> **⇐** Suppose $\Phi'$ has a satisfying assignment with exactly half of its variables True. It satisfies every clause of $\Phi'$, in particular the clauses of $\Phi$, which mention only the $x_i$. So its restriction to $x_1, \dots, x_n$ satisfies $\Phi$. (This direction does not even use the balance.)
>
> **Answer.** $\Phi$ is satisfiable if and only if $\Phi'$ has a satisfying assignment with exactly half of its variables True, and $\Phi'$ is built in polynomial time; so BalancedSat is NP-hard.

The two new clauses say $y_i = \bar x_i$, so *every* satisfying assignment of $\Phi'$ is balanced. A lazier padding also works: let $y_i$ occur only in the always-true clause $(y_i\vee\bar y_i)$; then a satisfying assignment of $\Phi$ with $t$ true variables is balanced by setting $n - t$ of the $y_i$ to True.

> [!trap] "Just hand over the same formula" is not a reduction
> Satisfiable does not imply balanced-satisfiable: $(x_1)\wedge(x_2)$ is satisfied only by making both variables True, and $(x_1\vee x_2\vee x_3)$ has an odd number of variables. A reduction must turn *every* satisfiable formula into a YES instance. Here the built formula for $(x_1)\wedge(x_2)$ has the single satisfying assignment $x_1 = x_2 = \textsf{True}$, $y_1 = y_2 = \textsf{False}$: two of four.

## Problem 3 — Exact3Sat

> [!question] Problem 3
> **Exact3Sat** (also called **OneIn3Sat**) asks whether a given CNF formula $\Phi$ with exactly three distinct literals per clause has an assignment such that **every clause contains exactly one True literal**. Prove that Exact3Sat is NP-hard.

> [!hint]- Hint
> Work clause by clause. For one clause $(a\vee b\vee c)$, find a few one-in-three clauses on $a, b, c$ and some new variables that can be completed exactly when $a\vee b\vee c$ is true. Putting $\bar a$ rather than $a$ into a gadget clause is useful: when $a$ is False, $\bar a$ uses up the clause's one true literal.

> [!solution]- Solution
> **The idea.** "Exactly one true literal" is a stronger demand than "at least one", so a satisfiable 3CNF formula need not be a YES instance of Exact3Sat as it stands; each clause has to be re-encoded. The gadget below has a middle clause $(b\vee v\vee w)$ that needs one true literal, and two outer clauses that *block* its helpers: $(\bar a\vee u\vee v)$ forces $v$ to be False when $a$ is False, and $(\bar c\vee w\vee t)$ forces $w$ to be False when $c$ is False. So if $a, b, c$ are all False, the middle clause has nothing left.
>
> **Reduce from** 3Sat.
>
> **Reduction.** Given an arbitrary 3CNF formula $\Phi$ with clauses $C_1, \dots, C_k$, introduce four new variables $u_j, v_j, w_j, t_j$ per clause and replace each clause $C_j = (a\vee b\vee c)$ by the three clauses
>
> $$
> (\bar a\vee u_j\vee v_j)\ \wedge\ (b\vee v_j\vee w_j)\ \wedge\ (\bar c\vee w_j\vee t_j).
> $$
>
> The result $\Phi'$ has $n + 4k$ variables and $3k$ clauses, each with three distinct literals, and is built in $O(k)$ time: **polynomial time**.
>
> **Gadget lemma.** For fixed truth values of $a, b, c$, the variables $u, v, w, t$ can be chosen so that each of the three clauses has exactly one true literal **if and only if** at least one of $a, b, c$ is True.
>
> *If $a, b, c$ are all False:* $\bar a$ is the true literal of the first clause, so $u = v = \textsf{False}$; $\bar c$ is the true literal of the third, so $w = t = \textsf{False}$; then the middle clause $(b\vee v\vee w)$ has no true literal. No choice works.
>
> *Otherwise,* choose as follows (all unlisted new variables False):
>
> | case | set | first clause | middle clause | third clause |
> |---|---|---|---|---|
> | $b$ True | $u = a$, $t = c$ | one of $\bar a, u$ | $b$ | one of $\bar c, t$ |
> | $b$ False, $a$ and $c$ True | $v$ and $t$ True | $v$ | $v$ | $t$ |
> | $b$ False, only $a$ True | $v$ True | $v$ | $v$ | $\bar c$ |
> | $b$ False, only $c$ True | $w$ True | $\bar a$ | $w$ | $w$ |
>
> In each row the last three columns name the one true literal of each clause.
>
> **⇒** Suppose an assignment satisfies $\Phi$. Every clause $C_j$ has a true literal, so by the lemma its four new variables can be set so that its three gadget clauses have exactly one true literal each. The gadgets of different clauses share no new variables, so all of them can be completed at once: $\Phi'$ is a YES instance of Exact3Sat.
>
> **⇐** Suppose an assignment gives every clause of $\Phi'$ exactly one true literal. For each $j$, the three gadget clauses of $C_j$ are completed, so by the lemma at least one literal of $C_j$ is True. The assignment, restricted to the variables of $\Phi$, satisfies $\Phi$.
>
> **Answer.** $\Phi$ is satisfiable if and only if $\Phi'$ has an assignment with exactly one true literal per clause, and $\Phi'$ is built in polynomial time; so Exact3Sat is NP-hard.

A one-in-three assignment is in particular a satisfying assignment, but not conversely: the four clauses $(x_1\vee x_2\vee x_3)$, $(\bar x_1\vee x_2\vee x_3)$, $(x_1\vee\bar x_2\vee x_3)$, $(x_1\vee x_2\vee\bar x_3)$ are satisfied by setting everything True, and have no one-in-three assignment. Exact3Sat is the "1-in-3Sat" of the book's list of useful NP-hard problems ([[2-algorithms/12-np-hardness#1213-other-useful-np-hard-problems|§12.13]]), a convenient starting point for problems about exact covers and partitions.

## Problem 4 — At most three literals, at most three occurrences (harder)

> [!question] Problem 4 (harder, to think about later)
> **(≤3,≤3)-Sat** is the special case of Sat in which every clause of the input formula contains **at most three literals**, and every variable appears in **at most three clauses**. Prove that (≤3,≤3)-Sat is NP-hard.

> [!hint]- Hint
> A variable that occurs too often can be replaced by several variables, one per occurrence — if you can force them all to be equal with short clauses that use each of them only twice.

> [!solution]- Solution
> **The idea.** In 3Sat a variable may occur in any number of clauses. Give each occurrence of a frequent variable its own copy; then each copy is in one clause, and has two occurrences to spare. Two occurrences are exactly enough to put the copies on a **cycle of implications** $x^1\Rightarrow x^2\Rightarrow\cdots\Rightarrow x^r\Rightarrow x^1$, which forces them to be all True or all False. An implication $p\Rightarrow q$ is the two-literal clause $(\bar p\vee q)$.
>
> **Reduce from** 3Sat.
>
> **Reduction.** Given an arbitrary 3CNF formula $\Phi$: for every variable $x$ that occurs $r > 3$ times in $\Phi$ (count every occurrence, positive or negated), introduce new variables $x^1, \dots, x^r$, replace the $j$-th occurrence of $x$ by $x^j$ (negated if the occurrence was negated), and add the $r$ clauses
>
> $$
> (\bar x^{1}\vee x^{2})\ \wedge\ (\bar x^{2}\vee x^{3})\ \wedge\ \cdots\ \wedge\ (\bar x^{r-1}\vee x^{r})\ \wedge\ (\bar x^{r}\vee x^{1}).
> $$
>
> Variables with at most three occurrences are left alone. In the result $\Phi'$, every clause has at most three literals, and every variable is in at most three clauses: an untouched variable as before, a copy $x^j$ in one old clause and in two clauses of its cycle. $\Phi$ has $3k$ literal occurrences, so there are at most $3k$ copies and at most $3k$ new clauses: $\Phi'$ has at most $4k$ clauses and is built in $O(k)$ time, **polynomial time**.
>
> **⇒** Suppose an assignment satisfies $\Phi$. Give every copy $x^j$ the value of $x$. Each old clause is satisfied as before, and each cycle clause $(\bar x^{j}\vee x^{j+1})$ is satisfied because its two variables are equal. So $\Phi'$ is satisfiable.
>
> **⇐** Suppose an assignment satisfies $\Phi'$. In the cycle of a variable $x$, if some copy $x^j$ is True then $(\bar x^{j}\vee x^{j+1})$ makes $x^{j+1}$ True, and so on around the cycle: all copies are True. Otherwise all are False. So all copies of $x$ have one common value; give $x$ that value (and keep the untouched variables). Every clause of $\Phi$ then evaluates exactly as its counterpart in $\Phi'$, which is satisfied. So $\Phi$ is satisfiable.
>
> **Example.** In $(x_1\vee x_2\vee x_3)\wedge(\bar x_1\vee x_2\vee x_4)\wedge(x_1\vee\bar x_3\vee x_4)\wedge(\bar x_1\vee\bar x_2\vee\bar x_4)$ only $x_1$ occurs more than three times. It gets four copies, one per clause, and the four cycle clauses $(\bar x_1^{1}\vee x_1^{2})$, $(\bar x_1^{2}\vee x_1^{3})$, $(\bar x_1^{3}\vee x_1^{4})$, $(\bar x_1^{4}\vee x_1^{1})$, which have exactly two satisfying assignments: all False and all True. The result has 8 clauses, and each copy is in exactly three of them.
>
> **Answer.** Replace the occurrences of every variable with more than three occurrences by separate copies joined by a cycle of two-literal implication clauses; $\Phi$ is satisfiable if and only if $\Phi'$ is, and $\Phi'$ is built in polynomial time. So (≤3,≤3)-Sat is NP-hard.

The cycle clauses have only two literals, which is why this problem allows *at most* three literals per clause. With exactly three, three occurrences are not enough — see the footnote discussed in Problem 5. Clauses of two literals read as implications are also the whole idea behind the polynomial-time algorithm for 2Sat ([[2-algorithms/12-np-hardness-exercises#exercise-126--two-is-easy|Exercise 12.6(c)]]).

## Problem 5 — Exactly three literals, at most four occurrences (harder)

> [!question] Problem 5 (harder, to think about later)
> **(3,≤4)-Sat** is the special case of Sat in which every clause of the input formula contains **exactly three distinct literals**, and every variable appears in **at most four clauses**. Prove that (3,≤4)-Sat is NP-hard. *(Hint: reduce from (≤3,≤3)-Sat.)*
>
> (The handout's footnote: the related problem (3,≤3)-Sat, with exactly three literals per clause and every variable in at most three clauses, is trivial — all such formulas are satisfiable.)

> [!hint]- Hint
> The short clauses of a (≤3,≤3)-Sat instance must be padded with new variables that are forced to be False — without touching the old variables again. Build a small formula with three distinct literals per clause that forces one of its variables to be False and uses that variable only three times.

> [!solution]- Solution
> **The idea.** A (≤3,≤3)-Sat instance fails to be a (3,≤4)-Sat instance only because some clauses are short. The padding of Problem 1 — $(a\vee b)$ becomes $(a\vee b\vee z)\wedge(a\vee b\vee\bar z)$ — would repeat $a$ and $b$, and a variable that sits in three short clauses would end up in six clauses. Instead, pad with a new variable $z$ that is **forced to be False** by a separate gadget, so that $(a\vee b\vee z)$ means $(a\vee b)$. The budget of four occurrences is what makes the gadget possible: $z$ appears once in the padded clause, so the gadget may use it three times.
>
> **The enforcer.** For a variable $z$ and three new variables $p, q, r$, let
>
> $$
> F(z)\ =\ (\bar z\vee\bar p\vee q)\wedge(\bar z\vee\bar q\vee r)\wedge(\bar z\vee\bar r\vee p)\wedge(p\vee q\vee r)\wedge(\bar p\vee\bar q\vee\bar r).
> $$
>
> *Lemma.* $F(z)$ is satisfiable, and every assignment that satisfies it sets $z$ to False.
>
> *Proof.* If $z$ is True, the first three clauses become $(\bar p\vee q)$, $(\bar q\vee r)$, $(\bar r\vee p)$: the cycle of implications $p\Rightarrow q\Rightarrow r\Rightarrow p$, which forces $p = q = r$ (Problem 4). But $(p\vee q\vee r)$ forbids all False and $(\bar p\vee\bar q\vee\bar r)$ forbids all True. So $z$ is False. With $z$ False the first three clauses are satisfied, and $p = \textsf{True}$, $q = r = \textsf{False}$ satisfies the last two. $\square$
>
> Every clause of $F(z)$ has three distinct literals; $z$ occurs in three of the five clauses, and each of $p, q, r$ in four.
>
> **Reduce from** (≤3,≤3)-Sat, which is NP-hard by Problem 4.
>
> **Reduction.** Given an arbitrary formula $\Psi$ in which every clause has at most three (distinct) literals and every variable is in at most three clauses:
> - a clause with three literals is kept;
> - a clause $(a\vee b)$ is replaced by $(a\vee b\vee z)$, together with the five clauses of $F(z)$, for a new variable $z$ (and new $p, q, r$);
> - a clause $(a)$ is replaced by $(a\vee z\vee z')$, together with $F(z)$ and $F(z')$, for new variables $z, z'$ (each with its own new $p, q, r$).
>
> In the result $\Psi'$ every clause has exactly three distinct literals. Every old variable is in as many clauses as before, at most three; every padding variable $z$ is in one padded clause and three clauses of its enforcer, four in all; every $p, q, r$ is in four. Each padding variable adds 5 clauses and 4 variables, and a clause needs at most two, so $\Psi'$ has at most 11 times as many clauses as $\Psi$ and is built in linear time: **polynomial time**.
>
> **⇒** Suppose an assignment satisfies $\Psi$. Set every padding variable to False and every enforcer's $(p, q, r)$ to $(\textsf{True}, \textsf{False}, \textsf{False})$. Each padded clause contains a clause of $\Psi$ and is satisfied by it; each enforcer is satisfied by the lemma. So $\Psi'$ is satisfiable.
>
> **⇐** Suppose an assignment satisfies $\Psi'$. It satisfies every enforcer, so by the lemma every padding variable is False. Each padded clause is satisfied, and not by its padding variables; so the clause of $\Psi$ inside it has a true literal. The assignment, restricted to the variables of $\Psi$, satisfies $\Psi$.
>
> **Answer.** Pad every short clause with new variables, each pinned to False by its own five-clause enforcer $F(z)$; $\Psi$ is satisfiable if and only if $\Psi'$ is, and $\Psi'$ is built in polynomial time. So (3,≤4)-Sat is NP-hard. Chained with Problem 4, this is a reduction 3Sat → (≤3,≤3)-Sat → (3,≤4)-Sat.

> [!note] Why three occurrences are not enough (the handout's footnote)
> If every clause has three distinct variables and every variable is in at most three clauses, then any $c$ clauses contain $3c$ variable occurrences, hence at least $c$ different variables. By Hall's marriage theorem (a standard fact about matchings, not part of this course), every clause can be given a variable of its own, a different one for each clause; set that variable to satisfy its clause. So every such formula is satisfiable, and the problem is trivial. The enforcer above could not exist with three occurrences per variable: it needs $p$, $q$ and $r$ four times each. The footnote does need clauses with three distinct *variables*: $(x\vee x\vee x)\wedge(\bar x\vee\bar x\vee\bar x)$ is unsatisfiable.

## Problem 6 — XorSat (harder)

> [!question] Problem 6 (harder, to think about later)
> A boolean formula is in **exclusive-or conjunctive normal form (XCNF)** if it is an And of one or more clauses, each of which is the **exclusive-or** of one or more literals. So a satisfying assignment of an XCNF formula makes an **odd number of literals True in every clause**. **XorSat** asks whether a given XCNF formula has a satisfying assignment. Describe a polynomial-time algorithm for XorSat.

> [!hint]- Hint
> Write True as 1 and False as 0. What is exclusive-or, as arithmetic? What is $\bar x$?

> [!solution]- Solution
> **The idea.** With $\textsf{True} = 1$ and $\textsf{False} = 0$, exclusive-or is addition modulo 2, and $\bar x = x + 1$. So a clause is a **linear equation modulo 2**: the clause $x_1\oplus\bar x_2\oplus x_3$ is true exactly when $x_1 + (x_2 + 1) + x_3\equiv 1$, that is, $x_1 + x_2 + x_3\equiv 0\pmod 2$. A whole formula is a system of linear equations, and such systems are solved by Gaussian elimination — over the integers modulo 2, where elimination needs no division, only adding one equation to another.
>
> **Algorithm.** Let the formula have clauses $C_1, \dots, C_m$ over variables $x_1, \dots, x_n$.
>
> ```text
> XorSat(Φ):
>     for i ← 1 to m                               ⟨⟨one equation per clause⟩⟩
>         A[i, j] ← 1 if x_j occurs an odd number of times in C_i, else 0     (for all j)
>         b[i] ← (1 + number of negated literals in C_i) mod 2
>     r ← 1                                        ⟨⟨rows 1 .. r − 1 have pivots⟩⟩
>     for j ← 1 to n
>         if A[i, j] = 1 for some row i ≥ r
>             swap rows i and r of A and of b
>             for every row i′ ≠ r with A[i′, j] = 1
>                 add row r to row i′, and b[r] to b[i′]        ⟨⟨modulo 2⟩⟩
>             pivot[r] ← j
>             r ← r + 1
>     if some row i has A[i, ·] all 0 and b[i] = 1
>         return None                              ⟨⟨the equation 0 = 1⟩⟩
>     x_j ← False for all j
>     for i ← 1 to r − 1
>         x_pivot[i] ← b[i]
>     return x
> ```
>
> **Correctness.** Clause $C_i$ has an odd number of true literals exactly when $\sum_j A[i, j]\,x_j\equiv b[i]\pmod 2$: each positive literal contributes its variable, each negated literal its variable plus 1, and a variable that occurs twice cancels. Swapping two equations or adding one to another does not change the set of solutions. At the end, each pivot column has a single 1, in its pivot row. If some row reads $0 = 1$, there is no solution. Otherwise every non-pivot ("free") variable may be set to 0, and each pivot row then reads $x_{\text{pivot}} = b$: the assignment returned satisfies every equation, hence every clause.
>
> **Time.** Building the system takes time linear in the formula. Each pivot costs at most $m$ row additions of length $n + 1$, and there are at most $\min(m, n)$ pivots: $O(mn\cdot\min(m, n))$ time, polynomial.
>
> **Examples.** $(x_1\oplus x_2)\wedge(x_2\oplus x_3)\wedge(x_1\oplus x_3)$ is unsatisfiable: the equations $x_1 + x_2 = 1$, $x_2 + x_3 = 1$, $x_1 + x_3 = 1$ add up to $0 = 1$. (As Or-clauses the same three clauses are satisfiable.) $(x_1\oplus\bar x_2\oplus x_3)\wedge(x_2\oplus x_3)\wedge(\bar x_1\oplus\bar x_3)$ becomes $x_1 + x_2 + x_3 = 0$, $x_2 + x_3 = 1$, $x_1 + x_3 = 1$, whose only solution is $x_1 = x_2 = \textsf{True}$, $x_3 = \textsf{False}$.
>
> **Answer.** Translate every clause into a linear equation modulo 2 and run Gaussian elimination; the formula is satisfiable if and only if no equation $0 = 1$ appears. $O(mn\cdot\min(m, n))$ time.

> [!exam] What this lab is for
> - **The write-up.** Problems 1–5 are graded by the [[0-toolkit/06-how-exams-are-graded#14-np-hardness|NP-hardness rubric]]: the known hard problem, a reduction that takes an *arbitrary* instance and nothing else, both directions of the proof, and the words "polynomial time". The direction is always **from** the known hard problem **to** the new one ([[concepts/polynomial-time-reductions]]).
> - **Local replacement.** Every reduction here handles one clause or one variable at a time with a small gadget, and the proofs are a lemma about one gadget plus "the gadgets do not interact". Count the size of what you build — it is the "polynomial time" point.
> - **A small change can flip the answer.** Three literals per clause with four occurrences per variable is NP-hard, with three occurrences trivial; Or-clauses are NP-hard, Xor-clauses are linear algebra; 3Sat is NP-hard, 2Sat polynomial ([[2-algorithms/12-np-hardness-exercises#exercise-126--two-is-easy|Exercise 12.6]]). "It looks like Sat" proves nothing in either direction.

### Sources for this page
CS/ECE 374 A (Fall 2026), Lab 12b handout, November 13; no official solutions were posted, so the solutions are ours. The reductions are the standard ones, written in our own words; the NP-hardness of Problem 5's variant and the fact in its footnote go back to Tovey (*A simplified NP-complete satisfiability problem*, 1984), and the five-clause enforcer is a compact form of the forcing gadgets used for bounded-occurrence Sat. Checked by `tools/checks/labs_12b.py`: each reduction is run on 700 3CNF formulas (497 satisfiable, 203 not; for Problem 2, 600 random CNF formulas; for Problem 5, 900 random formulas with short clauses, and the chain through Problem 4 on the 517 inputs with at most 15 clauses), the built formula is tested for its promised shape and size, and satisfiability is compared by exhaustive search or by a DPLL solver that is itself validated against exhaustive search; both certificate translations of every proof are executed; the gadget lemma of Problem 3 and the enforcer lemma of Problem 5 are checked on all assignments; the traps, the examples, the footnote's matching argument (400 random formulas) and the Gaussian elimination of Problem 6 (3,000 random XCNF formulas against exhaustive search) are checked as stated. Handout slips: "XNCF" for XCNF in Problem 6; "one special case of Sat this is still NP-hard" for "that is"; the footnote to Problem 5 says "exactly three literals" and needs them distinct, as in the problem itself — a clause that may repeat a literal breaks it.
