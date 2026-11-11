---
title: "Lectures, day by day"
description: "A log of what was covered in class in CS/ECE 374 A (Fall 2026), one page per lecture day, built from the transcripts of the lecture recordings: the date, the topics in the order they came up, the examples and problems worked, what was announced about homework and exams, and links to the chapter, concept and lab pages where each topic is explained."
tags: [lecture]
---

One page per lecture day, for every lecture whose recording transcript is in the course folder. Each page is a **record of the day, not a lesson**: the date, the announcements, the topics in the order they came up, the examples and problems worked in class, what the instructor said about homework, write-ups and exams, and a table of links to where this site explains each topic. Read the chapter and concept pages to learn the material; come here to see what a particular class covered, to find when something was said, or to catch up on a class you missed.

> [!note] How to read these pages
> - Everything is taken from the automatic transcript of the lecture recording and condensed. Text in a **quote** box, and any phrase in quotation marks, is what the instructor said, word for word as transcribed, with punctuation added; a word in [square brackets] replaces an obvious transcription error. Everything else is a summary in our words.
> - The transcripts carry no dates. Each page's date is worked out from what is announced at the start of the lecture (which homework is due "today", which lab is "tomorrow") and agrees with the dates of the labs, homeworks and exams elsewhere on this site; each page says how in its sources.
> - The slides and the board are not in a transcript, so a figure is described only as far as it was described aloud.

## Algorithms: graphs and shortest paths

| day | covered | worked in class | page |
|---|---|---|---|
| Tue Oct 20 | what a graph is; adjacency matrices and lists; reachability; whatever-first search; graph reductions and how to write one | useless states of a DFA | [[5-lecture-log/2026-10-20\|Oct 20]] |
| Thu Oct 22 | graph layering; parent pointers; queue, priority queue and stack as the bag; recursive depth-first search, DFSAll, pre and post; back edges | a walk of length divisible by 3 | [[5-lecture-log/2026-10-22\|Oct 22]] |
| Tue Oct 27 | cycle if and only if back edge; topological order as reverse postorder; single-source shortest paths: trees, Ford's relaxation, Dijkstra | cycle detection by finishing times | [[5-lecture-log/2026-10-27\|Oct 27]] |
| Thu Oct 29 | breadth-first search for unit weights; negative edges and cycles; shortest and longest paths in dags; memoization as postorder; an $O(VE)$ algorithm by layering | Lab 10a's negative edge revisited; shortest paths by layers | [[5-lecture-log/2026-10-29\|Oct 29]] |
| Tue Nov 3 | Bellman–Ford as a dynamic program; all-pairs shortest paths: repeated single-source, counting edges, halving, Floyd–Warshall | two derivations, no separate problem | [[5-lecture-log/2026-11-03\|Nov 3]] |

Thursday, November 5 was announced as an optional review session for Midterm 2 in place of the lecture, and Midterm 2 as Monday, November 9. Review of this block: [[0-toolkit/08-review-algorithms|the Midterm 2 review]].

## NP-hardness

| day | covered | worked in class | page |
|---|---|---|---|
| Tue Nov 10 | optimization and decision problems; problems as languages; many-one and Karp reductions; the lemma and its contrapositive; independent set, clique, vertex cover | independent set reduces to clique | [[5-lecture-log/2026-11-10\|Nov 10]] |

## What was announced, in one place

| said on | about | what |
|---|---|---|
| [[5-lecture-log/2026-10-20\|Oct 20]] | write-ups | a graph reduction states the graph, the problem solved on it and why, the algorithm called, and the running time in the input's own parameters; say "whatever-first search" unless the order matters |
| [[5-lecture-log/2026-10-22\|Oct 22]] | Homework 8 | Dijkstra's algorithm may be used as a black box in Problem 1 |
| [[5-lecture-log/2026-10-22\|Oct 22]] | scope | minimum spanning trees are not covered this semester |
| [[5-lecture-log/2026-10-27\|Oct 27]] | Midterm 2 | covers divide and conquer, dynamic programming and graphs; Homework 9 is the last homework before it |
| [[5-lecture-log/2026-10-27\|Oct 27]] | write-ups | do not cite Ford's generic algorithm; name the shortest-path algorithm that fits the graph |
| [[5-lecture-log/2026-10-29\|Oct 29]] | Midterm 2 | Monday, November 9, 7 pm; conflict exam the next morning |
| [[5-lecture-log/2026-10-29\|Oct 29]] | write-ups | "for all vertices $v$ in topological order" (or in postorder) is an acceptable line; the layered $O(VE)$ algorithm may be called Bellman–Ford |
| [[5-lecture-log/2026-11-03\|Nov 3]] | Midterm 2 | "mostly focusing on reductions"; Bellman–Ford and Floyd–Warshall are black boxes, their internals are not examined; three practice exams and review sessions |
| [[5-lecture-log/2026-11-10\|Nov 10]] | Homework 10 | due Tuesday, November 17; the second-to-last homework |
| [[5-lecture-log/2026-11-10\|Nov 10]] | write-ups | an NP-hardness reduction shows the algorithm, says "polynomial time", and proves both directions |

Related: [[2-algorithms/index|Part 2 · Algorithms]] · [[3-homework-and-exams/index|homework and exams]] · [[0-toolkit/06-how-exams-are-graded|how exams are graded]]

### Sources for this page
The six lecture-recording transcripts in the course folder (automatic transcripts, named by recording number), one per page above. Lectures before October 20 and the review session of November 5 have no transcript there.
