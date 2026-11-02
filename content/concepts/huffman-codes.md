---
title: "Huffman codes"
description: "Optimal prefix-free binary codes: code trees, the cost Σ f·depth, Huffman's rule of merging the two least frequent characters, why it is optimal, and its O(n log n) implementation with a priority queue."
tags: [concept, algorithms, greedy]
aliases: ["Huffman code", "Huffman's algorithm", "prefix-free code", "prefix code", "code tree", "BuildHuffman"]
---

> [!definition] Definition — prefix-free codes and Huffman's algorithm
> A binary code is **prefix-free** if no codeword is a prefix of another; equivalently, it is a binary **code tree** with the characters at the leaves, the codeword of a character being its root-to-leaf path (0 = left, 1 = right). For frequencies $f[1\,..\,n]$ the encoded message has length
> $$
> \textsf{cost}(T) = \sum_{i=1}^{n} f[i]\cdot\textsf{depth}_T(i) = \text{sum of the frequencies stored at the internal nodes}.
> $$
> **Huffman's algorithm:** merge the two least frequent characters into one whose frequency is their sum, and recurse; the merges build the tree bottom up. With a binary heap: $2n-1$ Inserts and $2n-2$ ExtractMins, $O(n\log n)$ time. Every Huffman tree has minimum cost.

**Why it works.** Exchange: in an optimal tree, moving a less frequent character to a deeper leaf never hurts, so the two least frequent characters $x, y$ can be placed as sibling leaves of maximum depth (Lemma 4.5). Merging them into one character $z$ with $f[z] = f[x]+f[y]$ turns any tree with $x, y$ siblings into a tree for the smaller alphabet whose cost is exactly $f[x]+f[y]$ less. So an optimal tree for the small alphabet, expanded at $z$, is optimal for the original — induction (Theorem 4.6).

> [!recipe] Recipe — building a Huffman code by hand
> 1. List the frequencies. Repeatedly remove the two smallest **current** values (merged nodes included), write their sum, and record the merge.
> 2. Draw the tree from the merges; label edges 0 (left) and 1 (right).
> 3. Cost check: total encoded length = sum of all the sums written in step 1 = $\sum f[i]\cdot\textsf{depth}(i)$.

> [!trap]
> - Merging the two smallest *original* frequencies instead of the two smallest current ones.
> - Expecting a unique answer: ties and left/right choices give different trees, even different codeword lengths, with the same cost.
> - Top-down splitting into halves of nearly equal weight (Fano–Shannon) is **not** optimal: $10, 4, 4, 4, 3$ costs 57 that way, 55 with Huffman.
> - A code tree is not a binary search tree: the leaves are unordered and only leaves hold characters.

**Example — ABRACADABRA.** Frequencies A 5, B 2, R 2, C 1, D 1. Merge C+D (2); now three 2s. Merging B+R (4), then CD+BR (6), then A+6 (11) gives lengths A 1, B 3, R 3, C 3, D 3; merging B+CD (4), then R+4 (6), then A+6 gives A 1, R 2, B 3, C 4, D 4. Both cost $2 + 4 + 6 + 11 = 23$ bits, against $3\cdot 11 = 33$ bits for a fixed-length code of 3 bits.

**Where it appears.** [[2-algorithms/04-greedy-algorithms#44-huffman-codes|§4.4]] (Sallows' sentence: 649 bits, Lemma 4.5, Theorem 4.6, BuildHuffman with its loop correction, encoding and decoding in $O(m)$); compare the cost function of [[concepts/optimal-binary-search-trees|optimal binary search trees]], where the keys must stay in order and dynamic programming is needed.

Related: [[concepts/greedy-algorithms]] · [[concepts/optimal-binary-search-trees]] · [[concepts/dynamic-programming]]
