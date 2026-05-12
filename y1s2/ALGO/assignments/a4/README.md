# Assignment 4 — Graph Optimization, Greedy Methods, and Dynamic Programming

## Requirements
- Python 3.8+ (no external libraries; only the standard library is used)

## Project Layout

```
ass4/
├── data/
│   ├── roads.csv       # Directed weighted road network  (Parts B1–B4)
│   ├── infra.csv       # Undirected weighted infrastructure graph  (Part C)
│   └── jobs.csv        # Job scheduling with rewards  (Part D)
├── src/
│   ├── b1_bfs.py               # B1 – BFS hop distance & path reconstruction
│   ├── b2_dfs.py               # B2 – DFS timestamps & edge classification
│   ├── b3_shortest_paths.py    # B3 – Dijkstra & Bellman-Ford
│   ├── b4_floyd_warshall.py    # B4 – Floyd-Warshall all-pairs shortest paths
│   ├── c1_prim.py              # C1 – Prim's MST
│   ├── d1_greedy_scheduling.py # D1 – Greedy interval scheduling (max count)
│   └── d2_weighted_dp.py       # D2 – Weighted interval scheduling (max reward)
└── report/
    └── report.tex              # Full written report (LaTeX)
```

## Running the Code

Run each script from the **project root** (`ass4/`):

```bash
# Part B – Graph Algorithms (roads.csv)
python3 src/b1_bfs.py
python3 src/b2_dfs.py
python3 src/b3_shortest_paths.py
python3 src/b4_floyd_warshall.py

# Part C – Network Design (infra.csv)
python3 src/c1_prim.py

# Part D – Scheduling (jobs.csv)
python3 src/d1_greedy_scheduling.py
python3 src/d2_weighted_dp.py
```

## Compiling the Report

```bash
cd report
pdflatex report.tex   # run twice for table of contents
```

## Algorithm Inventory

| Script | Algorithm | Complexity |
|--------|-----------|------------|
| b1_bfs.py | BFS | O(V + E) |
| b2_dfs.py | DFS | O(V + E) |
| b3_shortest_paths.py | Dijkstra | O((V+E) log V) |
| b3_shortest_paths.py | Bellman-Ford | O(VE) |
| b4_floyd_warshall.py | Floyd-Warshall | O(V³) |
| c1_prim.py | Prim's MST | O(E log V) |
| d1_greedy_scheduling.py | Greedy earliest-finish | O(n log n) |
| d2_weighted_dp.py | Weighted interval DP | O(n²) |

> No built-in graph algorithm implementations are used. Only standard Python
> data structures (heap, deque, dict, list) are used as building blocks.
