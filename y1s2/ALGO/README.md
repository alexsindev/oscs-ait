# Algorithm Design & Analysis (ALGO)

## Course Overview

Covers the design and rigorous analysis of algorithms — correctness proofs,
asymptotic complexity, and major algorithmic paradigms including greedy,
divide & conquer, dynamic programming, and graph algorithms.

## Topics

- Algorithm correctness: proof by induction, proof by contradiction, invariants
- Asymptotic notation: O, Ω, Θ, o, ω
- Sorting: insertion, merge, quick, heap, counting, radix, bucket sort
- Divide & conquer: recurrences, Master Theorem
- Greedy algorithms: interval scheduling, Huffman coding, MST (Prim, Kruskal)
- Dynamic programming: memoisation, tabulation, optimal substructure, overlapping sub-problems
- Graph algorithms: BFS, DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, MST
- Data structures: heaps, hash tables, BSTs, augmented trees, interval trees
- Amortised analysis

## Contents

```
ALGO/
├── notes/
│   ├── algorithm-design.md     General algorithm design principles
│   ├── proof-techniques.md     Proof by induction, contradiction, counter-example
│   ├── quicksort.md            Quicksort pseudocode + analysis
│   └── quicksort.py            Python implementation
├── assignments/
│   ├── a1/                     Greedy algorithms — interval scheduling
│   ├── a3/                     BST analysis notebook
│   └── a4/                     Graph algorithms (BFS, DFS, shortest paths, MST, scheduling DP)
│       ├── src/
│       │   ├── b1_bfs.py
│       │   ├── b2_dfs.py
│       │   ├── b3_shortest_paths.py
│       │   ├── b4_floyd_warshall.py
│       │   ├── c1_prim.py
│       │   ├── d1_greedy_scheduling.py
│       │   └── d2_weighted_dp.py
│       └── data/               CSV edge/job datasets
└── projects/
    └── travel-optimizer/       Tour planning optimizer (Greedy + Simulated Annealing)
```

## Projects

### Travel Optimizer — Final Project

Solves a **budget-constrained tour planning problem**: given a set of cities
with attractions, a total budget, and daily budget limits, find the tour that
maximises visitor satisfaction.

Two algorithms are implemented and benchmarked:
1. **Greedy** — cheapest feasible attraction first; O(n log n)
2. **Simulated Annealing** — probabilistic local search; escapes local optima

Comes with:
- FastAPI backend (`api/main.py`)
- Vite/React frontend with map view
- Benchmark experiments across dataset sizes
- Real Bangkok dataset + synthetic small/medium/large/hard sets

See [projects/travel-optimizer/](projects/travel-optimizer/) for full source.

## Assignment 4 — Graph Algorithms Summary

| File | Algorithm | Complexity |
|------|-----------|-----------|
| `b1_bfs.py` | BFS (hop distance) | O(V + E) |
| `b2_dfs.py` | DFS (topological / cycle detection) | O(V + E) |
| `b3_shortest_paths.py` | Dijkstra (weighted shortest path) | O((V+E) log V) |
| `b4_floyd_warshall.py` | Floyd-Warshall (all-pairs) | O(V³) |
| `c1_prim.py` | Prim's MST | O(E log V) |
| `d1_greedy_scheduling.py` | Greedy job scheduling | O(n log n) |
| `d2_weighted_dp.py` | Weighted interval scheduling DP | O(n log n) |
